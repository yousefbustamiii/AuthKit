from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.errors.domains.core_errors import OrgAccessDeniedError, OrgMemberNotFoundError, OrgRoleChangeNotAllowedError, OrgRoleChangeSelfError
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.store.sql.core.organizations.members.soft_delete_organization_member import soft_delete_organization_member
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

async def remove_organization_member(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    initiator_user_id: UUID,
    organization_id: UUID,
    target_user_id: UUID,
) -> None:
    initiator_membership = await resolve_user_role_in_org(pool, organization_id, initiator_user_id, org_role_cache)

    if initiator_membership.role not in ("owner", "admin"):
        raise OrgAccessDeniedError()

    if initiator_user_id == target_user_id:
        raise OrgRoleChangeSelfError()

    target_membership = await resolve_user_role_in_org(pool, organization_id, target_user_id, org_role_cache)

    if target_membership.role is None:
        raise OrgMemberNotFoundError()

    # owner can remove admin or member — admin can only remove members
    if initiator_membership.role == "admin" and target_membership.role != "member":
        raise OrgRoleChangeNotAllowedError()

    # owner cannot be removed via this route — only through ownership transfer
    if target_membership.role == "owner":
        raise OrgRoleChangeNotAllowedError()

    async with pool.acquire() as conn:
        await soft_delete_organization_member(conn, organization_id=organization_id, user_id=target_user_id)

    await RedisEventPublisher(cache).publish(
        "org_role:invalidation",
        "INVALIDATE_ORG_ROLE_CACHE",
        {"organization_id": str(organization_id), "user_id": str(target_user_id)},
    )
