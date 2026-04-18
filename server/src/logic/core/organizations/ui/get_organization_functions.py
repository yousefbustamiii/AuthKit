from uuid import UUID

from asyncpg import Pool

from server.src.store.sql.core.organizations.ui.get_user_organizations import UserOrganization, get_user_organizations


async def get_user_organizations_data(pool: Pool, user_id: UUID) -> list[UserOrganization]:
    async with pool.acquire() as conn:
        return await get_user_organizations(conn, user_id)
