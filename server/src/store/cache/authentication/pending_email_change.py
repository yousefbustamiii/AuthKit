from dataclasses import dataclass

from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.config.settings import settings

@dataclass
class PendingEmailChange:
    user_id: str
    new_email: str

async def store_pending_email_change(cache: Redis, lua_manager: LuaScriptManager, user_id: str, new_email: str) -> None:
    key = f"pending_email_change:{user_id}"
    competing_key = f"pending_deletion:{user_id}"

    await lua_manager.execute(
        "authentication/pending_email_change",
        [key, competing_key],
        [str(settings.otp.expire_minutes * 60), new_email]
    )

async def get_pending_email_change(cache: Redis, user_id: str) -> PendingEmailChange | None:
    key = f"pending_email_change:{user_id}"
    new_email = await cache.get(key)
    if new_email is None:
        return None
    return PendingEmailChange(user_id=user_id, new_email=new_email)

async def delete_pending_email_change(cache: Redis, user_id: str) -> None:
    key = f"pending_email_change:{user_id}"
    await cache.delete(key)
