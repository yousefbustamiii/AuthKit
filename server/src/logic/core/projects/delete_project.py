from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.errors.domains.core_errors import InvalidProjectNameError, OrgAccessDeniedError, ProjectNameMismatchError, ProjectNotFoundError
from server.src.app.validation.core.validate_core_names import validate_project_name
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org
from server.src.store.sql.core.projects.select_project_name import select_project_name
from server.src.store.sql.core.projects.soft_delete_project import soft_delete_project

async def delete_project(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
    project_id: UUID,
    name_confirmation: str,
) -> None:
    ok, result = validate_project_name(name_confirmation)
    if not ok:
        raise InvalidProjectNameError(result)

    validated_name = result

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
        project_name = await select_project_name(conn, project_id)

        if project_name is None:
            raise ProjectNotFoundError()

        if project_name != validated_name:
            raise ProjectNameMismatchError()

        await soft_delete_project(conn, project_id)
