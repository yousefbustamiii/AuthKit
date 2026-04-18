import asyncio
from typing import Any, AsyncGenerator

import orjson
import redis.asyncio as redis_module
from redis.asyncio import Redis

from server.src.app.config.settings import settings
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

REQUIRED_FIELDS = {"event_id", "event_type", "timestamp", "version", "payload"}

class RedisEventSubscriber:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def _create_pubsub_client(self) -> Redis:
        return redis_module.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=4,
            socket_timeout=None,
            socket_connect_timeout=7,
            health_check_interval=30,
        )

    def is_valid_envelope(self, data: dict[str, Any]) -> bool:
        return all(field in data for field in REQUIRED_FIELDS)

    async def listen(self, channel: str) -> AsyncGenerator[dict[str, Any], None]:
        while True:
            pubsub_client = None
            pubsub = None
            try:
                pubsub_client = self._create_pubsub_client()
                pubsub = pubsub_client.pubsub()
                await pubsub.subscribe(channel)
                logger.info("redis_pubsub_subscribed", extra={"channel": channel})

                async for message in pubsub.listen():
                    if message["type"] != "message":
                        continue

                    raw_data = message["data"]
                    if not isinstance(raw_data, (bytes, str)):
                        logger.warning(
                            "redis_pubsub_unexpected_data_type",
                            extra={"channel": channel, "type": type(raw_data)}
                        )
                        continue

                    try:
                        data = orjson.loads(raw_data)
                    except orjson.JSONDecodeError:
                        logger.error(
                            "redis_pubsub_json_decode_failed",
                            extra={"channel": channel, "raw_data": str(raw_data)[:200]}
                        )
                        continue

                    if not isinstance(data, dict) or not self.is_valid_envelope(data):
                        logger.warning(
                            "redis_pubsub_invalid_envelope_dropped",
                            extra={"channel": channel, "data": data}
                        )
                        continue

                    try:
                        yield data
                    except Exception:
                        logger.warning(
                            "redis_pubsub_consumption_failed_retrying",
                            extra={"channel": channel, "event_id": data.get("event_id")}
                        )
                        await asyncio.sleep(0.01)
                        try:
                            yield data
                        except Exception:
                            logger.exception(
                                "redis_pubsub_consumption_failed_permanently",
                                extra={"channel": channel, "event_id": data.get("event_id")}
                            )

            except (asyncio.CancelledError, StopAsyncIteration):
                raise
            except Exception:
                logger.exception("redis_pubsub_connection_lost", extra={"channel": channel})
                await asyncio.sleep(1.0)
            finally:
                if pubsub:
                    try:
                        await pubsub.unsubscribe(channel)
                        await pubsub.aclose()
                    except Exception:
                        pass
                if pubsub_client:
                    try:
                        await pubsub_client.aclose()
                    except Exception:
                        pass
