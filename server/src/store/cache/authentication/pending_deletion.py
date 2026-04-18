from dataclasses import dataclass

from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.config.settings import settings

@dataclass
class PendingDeletion:
    user_id: str
    email_hash: str

async def store_pending_deletion(cache: Redis, lua_manager: LuaScriptManager, user_id: str, email_hash: str) -> None:
    key = f"pending_deletion:{user_id}"
    competing_key = f"pending_email_change:{user_id}"

    await lua_manager.execute(
        "authentication/pending_deletion",
        [key, competing_key],
        [str(settings.otp.expire_minutes * 60), email_hash]
    )

async def get_pending_deletion(cache: Redis, user_id: str) -> PendingDeletion | None:
    key = f"pending_deletion:{user_id}"
    email_hash = await cache.get(key)
    if email_hash is None:
        return None
    return PendingDeletion(user_id=user_id, email_hash=email_hash)

async def delete_pending_deletion(cache: Redis, user_id: str) -> None:
    key = f"pending_deletion:{user_id}"
    await cache.delete(key)
