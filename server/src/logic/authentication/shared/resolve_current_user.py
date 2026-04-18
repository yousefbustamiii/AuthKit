from asyncpg import Pool

from server.src.store.sql.authentication.users.select_authenticated_user import AuthenticatedUser, select_authenticated_user

async def resolve_current_user(pool: Pool, session_token: str) -> AuthenticatedUser | None:
    async with pool.acquire() as conn:
        return await select_authenticated_user(conn, session_token)
