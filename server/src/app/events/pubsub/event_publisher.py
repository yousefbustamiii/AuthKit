import asyncio
from dataclasses import dataclass, field
import time
from typing import Any
import uuid

import orjson
from redis.asyncio import Redis

from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

@dataclass(frozen=True)
class PubSubEvent:
    event_type: str
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid7()))
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    version: int = 1

    def to_json(self) -> bytes:
        return orjson.dumps({
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "version": self.version,
            "payload": self.payload,
        })


class RedisEventPublisher:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def publish(self, channel: str, event_type: str, payload: dict[str, Any]) -> int:

        event = PubSubEvent(event_type=event_type, payload=payload)
        event_json = event.to_json()

        try:
            return await self.redis.publish(channel, event_json)
        except Exception:
            await asyncio.sleep(0.01)
            try:
                return await self.redis.publish(channel, event_json)
            except Exception:
                logger.exception(
                    "redis_pubsub_publish_failed_after_retry",
                    extra={
                        "channel": channel,
                        "event_type": event_type,
                        "event_id": event.event_id
                    }
                )
                return 0
