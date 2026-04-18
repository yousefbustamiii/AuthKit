import asyncio

from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.events.pubsub.event_subscriber import RedisEventSubscriber
from server.src.app.logging.logger_setup import get_logger
from server.src.store.cache.core.api_key_redis_cache import delete_redis_api_key
from server.src.store.cache.core.memory.api_key_memory_cache import delete_memory_api_key

logger = get_logger(__name__)

API_KEY_INVALIDATION_CHANNEL = "api_key:invalidation"
INVALIDATE_API_KEY_CACHE = "INVALIDATE_API_KEY_CACHE"


async def api_key_cache_invalidation_listener(redis: Redis, org_api_key_cache: TTLCache) -> None:
    subscriber = RedisEventSubscriber(redis)
    async for event in subscriber.listen(API_KEY_INVALIDATION_CHANNEL):
        try:
            event_type = event["event_type"]

            if event_type == INVALIDATE_API_KEY_CACHE:
                key_hash = event["payload"].get("key_hash")

                if not key_hash:
                    logger.warning(
                        "api_key_invalidation_missing_key_hash",
                        extra={"event_id": event.get("event_id")},
                    )
                    continue

                # Invalidate Memory (L1)
                delete_memory_api_key(org_api_key_cache, key_hash)

                # Invalidate Redis (L2)
                await delete_redis_api_key(redis, key_hash)

        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception(
                "api_key_cache_invalidation_listener_failed",
                extra={"event_id": event.get("event_id")},
            )
