from uuid import UUID

from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.events.event_emitter import event_emitter
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

async def expire_all_redis_sessions(cache: Redis, lua_manager: LuaScriptManager, user_id: UUID, emit_on_error: bool = True) -> None:
    user_key = f"user_sessions:{user_id}"

    try:
        await lua_manager.execute("authentication/expire_all_redis_sessions", [user_key], [])
    except Exception:
        if emit_on_error:
            logger.warning("expire_all_redis_sessions_failed_emitting_event", extra={"user_id": str(user_id)})
            await event_emitter(
                cache,
                "USER_SESSIONS_EXPIRE_FAILED",
                {"user_id": str(user_id)}
            )
        else:
            logger.warning("expire_all_redis_sessions_failed", extra={"user_id": str(user_id)})
            raise
