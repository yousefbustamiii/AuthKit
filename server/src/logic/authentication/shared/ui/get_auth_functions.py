from uuid import UUID

from asyncpg import Pool

from server.src.store.sql.authentication.devices.ui.get_all_user_devices import UserDevice, get_all_user_devices
from server.src.store.sql.authentication.sessions.ui.get_all_user_sessions import UserSession, get_all_user_sessions
from server.src.store.sql.authentication.users.ui.get_all_user_profile import UserProfile, get_user_profile

async def get_user_profile_data(pool: Pool, user_id: UUID) -> UserProfile | None:
    async with pool.acquire() as conn:
        return await get_user_profile(conn, user_id)

async def get_user_sessions_data(pool: Pool, user_id: UUID) -> list[UserSession]:
    async with pool.acquire() as conn:
        return await get_all_user_sessions(conn, user_id)

async def get_user_devices_data(pool: Pool, user_id: UUID) -> list[UserDevice]:
    async with pool.acquire() as conn:
        return await get_all_user_devices(conn, user_id)
