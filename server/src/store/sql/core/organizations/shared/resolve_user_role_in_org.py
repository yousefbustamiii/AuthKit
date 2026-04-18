from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache

from server.src.store.cache.core.memory.org_role_memory_cache import get_memory_org_role, set_memory_org_role
from server.src.store.sql.core.organizations.select_user_role_in_org import UserRoleInOrg, select_user_role_in_org

async def resolve_user_role_in_org(
    pool: Pool,
    organization_id: UUID,
    user_id: UUID,
    org_role_cache: TTLCache,
) -> UserRoleInOrg:
    # L1: In-Memory TTL Cache Check
    memory_role = get_memory_org_role(org_role_cache, organization_id, user_id)
    if memory_role is not None:
        return memory_role

    # L2: PostgreSQL Database Check
    async with pool.acquire() as conn:
        db_role = await select_user_role_in_org(conn, organization_id, user_id)

    # Hydrate L1
    set_memory_org_role(org_role_cache, organization_id, user_id, db_role)

    return db_role
