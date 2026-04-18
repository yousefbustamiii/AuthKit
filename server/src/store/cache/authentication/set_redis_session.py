from datetime import datetime
from uuid import UUID

from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

async def set_redis_session(
    cache: Redis,
    lua_manager: LuaScriptManager,
    session_token: str,
    session_id: UUID,
    user_id: UUID,
    expires_at: datetime,
    account_status: str = "active",
    device_id: UUID | None = None,
) -> None:
    session_token_hash = hash_blake2s(session_token)
    ttl_seconds = 86400

    session_key = f"session:{session_token_hash}"
    user_key = f"user_sessions:{user_id}"
    device_key = f"device_sessions:{device_id}" if device_id else ""

    try:
        await lua_manager.execute(
            "authentication/set_redis_session",
            [session_key, user_key, device_key],
            [
                session_token_hash,
                str(session_id),
                str(user_id),
                expires_at.isoformat(),
                account_status,
                str(device_id) if device_id else "",
                str(ttl_seconds),
            ]
        )
    except Exception:
        logger.warning("set_redis_session_failed", extra={"user_id": str(user_id)})
