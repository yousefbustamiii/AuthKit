from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.config.settings import settings
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.crypto.secrets.generate_otp import generate_otp

async def refresh_otp(cache: Redis, lua_manager: LuaScriptManager, email_hash: str) -> str | None:
    key = f"otp:{email_hash}"
    new_otp = generate_otp()
    new_otp_hash = hash_blake2s(new_otp)
    ttl = settings.otp.expire_minutes * 60

    result = await lua_manager.execute("authentication/refresh_otp", [key], [ttl, new_otp_hash])

    if result is None:
        return None

    return new_otp

