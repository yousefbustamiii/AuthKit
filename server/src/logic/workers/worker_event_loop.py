import asyncio
from typing import Awaitable, Callable

from redis.asyncio import Redis

from server.src.app.events.event_consumer import event_consumer
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

async def run_worker_loop(
    redis: Redis,
    handlers: dict[str, Callable[[dict], Awaitable[None]]]
) -> None:
    while True:
        try:
            await event_consumer(redis, handlers)
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("worker_loop_critical_failure")
            await asyncio.sleep(1)