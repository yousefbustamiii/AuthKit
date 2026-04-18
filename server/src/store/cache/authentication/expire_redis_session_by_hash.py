from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.events.event_emitter import event_emitter
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

async def expire_redis_session_by_hash(cache: Redis, lua_manager: LuaScriptManager, session_token_hash: str, emit_on_error: bool = True) -> None:
    try:
        await lua_manager.execute("authentication/expire_redis_session_by_hash", [], [session_token_hash])
    except Exception:
        if emit_on_error:
            logger.warning("expire_redis_session_by_hash_failed_emitting_event")
            await event_emitter(
                cache,
                "SESSION_HASH_EXPIRE_FAILED",
                {"session_token_hash": session_token_hash}
            )
        else:
            logger.warning("expire_redis_session_by_hash_failed")
            raise
