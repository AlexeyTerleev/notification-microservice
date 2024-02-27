import logging
import aio_pika
import asyncio
import bson

from app.config import settings

logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)


async def on_message(message) -> None:
    try:
        await process_message(message)
        raise TypeError("test")
        await message.ack()
    except Exception as e:
        redelivered_count = message.headers.get('x-delivery-count', 0)
        if redelivered_count < 5:
            logging.warning(
                f"Message (id = {message.message_id}) raise exeption (attemp {redelivered_count})."
            )
            await message.reject(requeue=True)
        else:
            logging.warning(
                f"Message (id = {message.message_id}) moved to dead letter queue."
            )
            await move_to_dead_letter_queue(message)

async def process_message(message) -> None:
    logging.info(f"Received message body: {bson.decode(message.body)}")
    logging.info(f"message: {message}")
    logging.info(f"Message delivery_tag: {message.delivery_tag}")


async def move_to_dead_letter_queue(message):
    connection = await aio_pika.connect(settings.rabbit_mq.get_url())
    async with connection:
        channel = await connection.channel()
        dead_letter_queue = await channel.declare_queue("dead_letter", durable=True)
        await dead_letter_queue.publish(message.body, headers=message.headers)



async def main():
    connection = await aio_pika.connect_robust(settings.rabbit_mq.get_url())

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(settings.rabbit_mq.RESET_PASSWORD_QUEUE, durable=True, arguments={"x-queue-type": "quorum"})
        await queue.consume(on_message)

        await asyncio.Future()


if __name__ == "__main__": 
    logging.info("running")
    asyncio.run(main())