from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache

from server.src.app.errors.domains.core_errors import OrgAccessDeniedError
from server.src.store.sql.core.organizations.members.ui.get_organization_invitations import OrganizationInvitationRecord, get_organization_invitations
from server.src.store.sql.core.organizations.members.ui.get_organization_members import OrganizationMemberRecord, get_organization_members
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org


async def get_organization_members_data(
    pool: Pool,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
) -> list[OrganizationMemberRecord]:
    membership = await resolve_user_role_in_org(pool, organization_id, user_id, org_role_cache)
    if membership.role is None:
        raise OrgAccessDeniedError()

    async with pool.acquire() as conn:
        return await get_organization_members(conn, organization_id)

async def get_organization_invitations_data(
    pool: Pool,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
) -> list[OrganizationInvitationRecord]:
    membership = await resolve_user_role_in_org(pool, organization_id, user_id, org_role_cache)
    if membership.role is None:
        raise OrgAccessDeniedError()

    async with pool.acquire() as conn:
        return await get_organization_invitations(conn, organization_id)
