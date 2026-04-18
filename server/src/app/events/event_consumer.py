import asyncio
from typing import Awaitable, Callable

import orjson
from redis.asyncio import Redis

from server.src.app.events.event_emitter import OutboundEvent
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

async def event_consumer(
    redis: Redis,
    handlers: dict[str, Callable[[dict], Awaitable[None]]]
) -> None:
    try:
        result = await redis.brpop("events:queue", timeout=3)
        if not result:
            return
        
        _, raw_data = result
        data = orjson.loads(raw_data)
        
        event = OutboundEvent(
            event=data["event"],
            event_token=data["event_token"],
            payload=data["payload"]
        )
            
    except orjson.JSONDecodeError as e:
        logger.critical("malformed_event_dropped", extra={"error": str(e), "raw": raw_data[:200]})
        return
    except (KeyError, TypeError) as e:
        logger.critical("incomplete_event_dropped", extra={"error": str(e), "raw": raw_data[:200]})
        return
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("redis_queue_consume_error")
        await asyncio.sleep(0.1)
        return

    if event.event_token:
        idempotency_key = f"event:processed:{event.event_token}"
        is_new = await redis.set(idempotency_key, "1", nx=True, ex=21600)
        
        if not is_new:
            return

    handler = handlers.get(event.event)
    if not handler:
        logger.warning("unknown_event", extra={"event": event.event})
        return

    try:
        await handler(event.payload)
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("event_handler_failed", extra={"event": event.event})
        
        await asyncio.sleep(0.1)
        await redis.rpush("events:queue", raw_data)
        
        if event.event_token:
            await redis.delete(f"event:processed:{event.event_token}")

    return