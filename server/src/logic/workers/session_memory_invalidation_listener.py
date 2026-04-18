import asyncio
from uuid import UUID

from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.events.pubsub.event_subscriber import RedisEventSubscriber
from server.src.app.logging.logger_setup import get_logger
from server.src.store.cache.authentication.memory.session_memory_cache import delete_memory_session, delete_memory_sessions_by_devices, delete_memory_sessions_by_user, delete_memory_sessions_by_user_except

logger = get_logger(__name__)

SESSION_INVALIDATION_CHANNEL = "session:invalidation"
EXPIRE_SINGLE_SESSION_MEMORY = "EXPIRE_SINGLE_SESSION_MEMORY"
EXPIRE_USER_SESSIONS_MEMORY = "EXPIRE_USER_SESSIONS_MEMORY"
EXPIRE_DEVICE_SESSIONS_MEMORY = "EXPIRE_DEVICE_SESSIONS_MEMORY"
EXPIRE_USER_SESSIONS_EXCEPT_MEMORY = "EXPIRE_USER_SESSIONS_EXCEPT_MEMORY"


async def session_memory_invalidation_listener(redis: Redis, session_cache: TTLCache) -> None:
    subscriber = RedisEventSubscriber(redis)
    async for event in subscriber.listen(SESSION_INVALIDATION_CHANNEL):
        try:
            event_type = event["event_type"]

            if event_type == EXPIRE_SINGLE_SESSION_MEMORY:
                session_token_hash = event["payload"].get("session_token_hash")
                if not session_token_hash:
                    logger.warning(
                        "session_memory_invalidation_missing_token_hash",
                        extra={"event_id": event.get("event_id")},
                    )
                    continue
                delete_memory_session(session_cache, session_token_hash)

            elif event_type == EXPIRE_USER_SESSIONS_MEMORY:
                raw_user_id = event["payload"].get("user_id")
                if not raw_user_id:
                    logger.warning(
                        "session_memory_invalidation_missing_user_id",
                        extra={"event_id": event.get("event_id")},
                    )
                    continue
                delete_memory_sessions_by_user(session_cache, UUID(raw_user_id))

            elif event_type == EXPIRE_DEVICE_SESSIONS_MEMORY:
                raw_device_ids = event["payload"].get("device_ids")
                if not raw_device_ids:
                    logger.warning(
                        "session_memory_invalidation_missing_device_ids",
                        extra={"event_id": event.get("event_id")},
                    )
                    continue
                device_ids = {UUID(d) for d in raw_device_ids}
                delete_memory_sessions_by_devices(session_cache, device_ids)

            elif event_type == EXPIRE_USER_SESSIONS_EXCEPT_MEMORY:
                raw_user_id = event["payload"].get("user_id")
                session_token_hash_to_keep = event["payload"].get("session_token_hash")
                if not raw_user_id or not session_token_hash_to_keep:
                    logger.warning(
                        "session_memory_invalidation_missing_fields",
                        extra={"event_id": event.get("event_id")},
                    )
                    continue
                delete_memory_sessions_by_user_except(session_cache, UUID(raw_user_id), session_token_hash_to_keep)

        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception(
                "session_memory_invalidation_handler_failed",
                extra={"event_id": event.get("event_id")},
            )
