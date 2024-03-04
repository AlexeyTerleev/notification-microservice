import logging
import asyncio

from app.config import setup_logging
from app.constants import APP_RUNNING
from services.consume_service import ConsumeService


async def main():
    consume_service = ConsumeService()
    await consume_service.start_consume()


if __name__ == "__main__": 

    setup_logging()

    logging.info(APP_RUNNING)
    asyncio.run(main())