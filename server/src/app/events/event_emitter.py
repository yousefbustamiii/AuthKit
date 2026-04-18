from dataclasses import dataclass

import orjson
from redis.asyncio import Redis

from server.src.app.crypto.tokens.event_tokens import generate_event_token
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

@dataclass
class OutboundEvent:
    event: str
    event_token: str
    payload: dict

async def event_emitter(redis: Redis, event_name: str, payload: dict) -> None:
    token = generate_event_token()
    
    event_data = {
        "event": event_name,
        "event_token": token,
        "payload": payload
    }
    
    try:
        await redis.lpush("events:queue", orjson.dumps(event_data))
    except Exception:
        logger.exception(
            "redis_event_push_failed",
            extra={
                "event": event_name,
                "event_token": token
            }
        )