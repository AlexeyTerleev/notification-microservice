import asyncio
import aio_pika
import logging
import bson
import pymongo
import motor.motor_asyncio

from app.config import settings
from app.services.email_service import EmailService
from app.constants import (
    MESSAGE_RECIVED,
    MESSAGE_PROCESSED,
    MESSAGE_RISED_EXCEPTION,
    MESSAGE_RETRY,
    MESSAGE_REDIRECTED_TO_DLQ,
)


class ConsumeService:

    def __init__(self) -> None:
        self.rabbitmq_url = settings.rabbit_mq.url
        self.reset_password_queue_name = settings.rabbit_mq.RESET_PASSWORD_QUEUE
        self.dead_letter_queue_name = settings.rabbit_mq.DEAD_LETTER_QUEUE

        self.email_service = EmailService()
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongo_db.url, 
            read_preference=pymongo.ReadPreference.PRIMARY
        )

    async def start_consume(self):
        connection = await self.get_rabbitmq_connection()
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue(
                self.reset_password_queue_name, 
                durable=True, 
                arguments={"x-queue-type": "quorum"}
            )
            await queue.consume(self.on_message)
            await asyncio.Future()

    async def on_message(self, message) -> None:
        logging.info(MESSAGE_RECIVED.format(message.message_id))
        try:
            await self.process_message(message)
            logging.info(MESSAGE_PROCESSED.format(message.message_id))
        except Exception as e:
            logging.warning(MESSAGE_RISED_EXCEPTION.format(message.message_id, e))
            await self.redirect_message(message)            

    async def process_message(self, message) -> None:
        payload = bson.decode(message.body)
        session = await self.mongo_client.start_session()
        try:
            await self.execute_transaction(session, payload)
        except Exception as e:
            raise e
        finally:
            await session.end_session()
        await message.ack()

    async def redirect_message(self, message):
        delivery_count = message.headers.get('x-delivery-count', 0)
        if delivery_count < 5:
            logging.error(MESSAGE_RETRY.format(message.message_id, delivery_count))
            await message.reject(requeue=True)
        else:
            logging.error(MESSAGE_REDIRECTED_TO_DLQ.format(message.message_id))
            await self.move_to_dead_letter_queue(message)
            await message.reject()

    async def execute_transaction(self, session, payload):
        collection = self.mongo_client.main_db.reset_password
        session.start_transaction()
        try: 
            await collection.insert_one(payload, session=session)
            await self.email_service.send_reset_password_url(
                payload["email"], 
                payload["reset_password_url"],
            )
        except Exception as e:
            session.abort_transaction()
            raise e
        else:
            session.commit_transaction()

    async def move_to_dead_letter_queue(self, message):
        connection = await self.get_rabbitmq_connection()
        async with connection:
            channel = await connection.channel()
            dead_letter_queue = await channel.declare_queue(
                self.dead_letter_queue_name, 
                durable=True,
            )
            await channel.default_exchange.publish(
                message, 
                routing_key=dead_letter_queue.name,
            )

    async def get_rabbitmq_connection(self):
        return await aio_pika.connect(self.rabbitmq_url)


    