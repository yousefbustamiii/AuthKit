from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.errors.domains.core_errors import InvalidRevokeConfirmationError, OrgAccessDeniedError
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.logic.workers.api_key_cache_invalidation_listener import API_KEY_INVALIDATION_CHANNEL, INVALIDATE_API_KEY_CACHE
from server.src.store.sql.core.api_keys.soft_delete_api_key import soft_delete_api_key
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

async def revoke_project_api_key(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
    project_id: UUID,
    key_id: UUID,
    confirmation: str,
) -> None:
    if confirmation.lower() != "revoke":
        raise InvalidRevokeConfirmationError()

    role_result = await resolve_user_role_in_org(
        pool=pool,
        organization_id=organization_id,
        user_id=user_id,
        org_role_cache=org_role_cache,
    )

    if role_result.role is None:
        raise OrgAccessDeniedError()

    if role_result.role not in ("owner", "admin"):
        raise OrgAccessDeniedError()

    async with pool.acquire() as conn:
        revoked_key_hash = await soft_delete_api_key(conn, key_id, project_id)

    if revoked_key_hash:
        await RedisEventPublisher(cache).publish(
            API_KEY_INVALIDATION_CHANNEL,
            INVALIDATE_API_KEY_CACHE,
            {"key_hash": revoked_key_hash},
        )
