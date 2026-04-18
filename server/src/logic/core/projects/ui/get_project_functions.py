from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache

from server.src.app.errors.domains.core_errors import OrgAccessDeniedError
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org
from server.src.store.sql.core.projects.ui.get_organization_projects import OrganizationProjectRecord, get_organization_projects


async def get_organization_projects_data(
    pool: Pool,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
) -> list[OrganizationProjectRecord]:
    membership = await resolve_user_role_in_org(pool, organization_id, user_id, org_role_cache)
    if membership.role is None:
        raise OrgAccessDeniedError()

    async with pool.acquire() as conn:
        return await get_organization_projects(conn, organization_id)
