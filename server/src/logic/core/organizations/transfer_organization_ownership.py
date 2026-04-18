from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.errors.domains.core_errors import InvalidOrgNameError, OrgAccessDeniedError, OrgLastOwnedError, OrgTransferNameMismatchError, OrgTransferTargetNotFoundError, OrgTransferToSelfError
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.app.validation.core.validate_core_names import validate_org_name
from server.src.store.sql.core.organizations.members.roles.update_organization_member_role import update_organization_member_role
from server.src.store.sql.core.organizations.select_organization_name import select_organization_name
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org
from server.src.store.sql.core.organizations.update_organization_owner import update_organization_owner

async def transfer_organization_ownership(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    initiator_user_id: UUID,
    organization_id: UUID,
    target_user_id: UUID,
    organization_name: str,
) -> None:
    ok, result = validate_org_name(organization_name)
    if not ok:
        raise InvalidOrgNameError(result)

    validated_name = result

    initiator_membership = await resolve_user_role_in_org(pool, organization_id, initiator_user_id, org_role_cache)

    if initiator_membership.role != "owner":
        raise OrgAccessDeniedError()

    if initiator_membership.owned_org_count <= 1:
        raise OrgLastOwnedError()

    if initiator_user_id == target_user_id:
        raise OrgTransferToSelfError()

    target_membership = await resolve_user_role_in_org(pool, organization_id, target_user_id, org_role_cache)

    if target_membership.role is None:
        raise OrgTransferTargetNotFoundError()

    async with pool.acquire() as conn:
        org_name = await select_organization_name(conn, organization_id=organization_id)

        if org_name is None or org_name != validated_name:
            raise OrgTransferNameMismatchError()

        async with conn.transaction():
            await update_organization_member_role(conn, organization_id=organization_id, user_id=initiator_user_id, role="admin")
            await update_organization_member_role(conn, organization_id=organization_id, user_id=target_user_id, role="owner")
            await update_organization_owner(conn, organization_id=organization_id, owner_user_id=target_user_id)

    publisher = RedisEventPublisher(cache)
    await publisher.publish(
        "org_role:invalidation",
        "INVALIDATE_USER_ORG_ROLES",
        {"user_id": str(initiator_user_id)},
    )
    await publisher.publish(
        "org_role:invalidation",
        "INVALIDATE_USER_ORG_ROLES",
        {"user_id": str(target_user_id)},
    )
