import asyncio
from uuid import UUID

from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.events.pubsub.event_subscriber import RedisEventSubscriber
from server.src.app.logging.logger_setup import get_logger
from server.src.store.cache.core.memory.org_role_memory_cache import delete_all_memory_org_roles_for_user, delete_all_memory_users_for_org_role, delete_memory_org_role

logger = get_logger(__name__)

ORG_ROLE_INVALIDATION_CHANNEL = "org_role:invalidation"
INVALIDATE_ORG_ROLE_CACHE = "INVALIDATE_ORG_ROLE_CACHE"
INVALIDATE_USER_ORG_ROLES = "INVALIDATE_USER_ORG_ROLES"
INVALIDATE_ORG_ALL_ROLES = "INVALIDATE_ORG_ALL_ROLES"


async def org_role_cache_invalidation_listener(redis: Redis, org_role_cache: TTLCache) -> None:
    subscriber = RedisEventSubscriber(redis)
    async for event in subscriber.listen(ORG_ROLE_INVALIDATION_CHANNEL):
        try:
            event_type = event["event_type"]

            if event_type == INVALIDATE_ORG_ROLE_CACHE:
                raw_org_id = event["payload"].get("organization_id")
                raw_user_id = event["payload"].get("user_id")

                if not raw_org_id or not raw_user_id:
                    logger.warning(
                        "org_role_invalidation_missing_fields",
                        extra={"event_id": event.get("event_id")},
                    )
                    continue

                delete_memory_org_role(org_role_cache, UUID(raw_org_id), UUID(raw_user_id))

            elif event_type == INVALIDATE_USER_ORG_ROLES:
                raw_user_id = event["payload"].get("user_id")

                if not raw_user_id:
                    logger.warning(
                        "org_role_invalidation_missing_user_id",
                        extra={"event_id": event.get("event_id")},
                    )
                    continue

                delete_all_memory_org_roles_for_user(org_role_cache, UUID(raw_user_id))

            elif event_type == INVALIDATE_ORG_ALL_ROLES:
                raw_org_id = event["payload"].get("organization_id")

                if not raw_org_id:
                    logger.warning(
                        "org_role_invalidation_missing_org_id",
                        extra={"event_id": event.get("event_id")},
                    )
                    continue

                delete_all_memory_users_for_org_role(org_role_cache, UUID(raw_org_id))

        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception(
                "org_role_cache_invalidation_listener_failed",
                extra={"event_id": event.get("event_id")},
            )
