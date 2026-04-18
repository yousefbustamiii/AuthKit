import asyncio
import random

from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

async def handle_dummy_email(payload: dict) -> None:
    logger.info("dummy_email_event_received", extra={"payload": payload})
    delay = random.uniform(0.015, 0.08)
    await asyncio.sleep(delay)
