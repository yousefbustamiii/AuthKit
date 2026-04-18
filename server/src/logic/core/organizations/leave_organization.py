from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.errors.domains.core_errors import OrgAccessDeniedError, OrgOwnerCannotLeaveError
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.store.sql.core.organizations.members.soft_delete_organization_member import soft_delete_organization_member
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

async def leave_organization(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
) -> None:
    membership = await resolve_user_role_in_org(pool, organization_id, user_id, org_role_cache)

    if membership.role is None:
        raise OrgAccessDeniedError()

    if membership.role == "owner":
        raise OrgOwnerCannotLeaveError()

    async with pool.acquire() as conn:
        await soft_delete_organization_member(conn, organization_id=organization_id, user_id=user_id)

    await RedisEventPublisher(cache).publish(
        "org_role:invalidation",
        "INVALIDATE_ORG_ROLE_CACHE",
        {"organization_id": str(organization_id), "user_id": str(user_id)},
    )
