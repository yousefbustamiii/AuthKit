from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.errors.domains.core_errors import InvalidOrgNameError, OrgAccessDeniedError
from server.src.app.validation.core.validate_core_names import validate_org_name
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org
from server.src.store.sql.core.organizations.update_organization import update_organization

async def edit_organization(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
    name: str,
) -> None:
    ok, result = validate_org_name(name)
    if not ok:
        raise InvalidOrgNameError(result)

    membership = await resolve_user_role_in_org(pool, organization_id, user_id, org_role_cache)

    if membership.role != "owner":
        raise OrgAccessDeniedError()

    async with pool.acquire() as conn:
        await update_organization(conn, organization_id=organization_id, name=result)
