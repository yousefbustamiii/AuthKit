from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.events.event_emitter import event_emitter
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

async def expire_redis_session(cache: Redis, lua_manager: LuaScriptManager, session_token: str, emit_on_error: bool = True) -> None:
    session_token_hash = hash_blake2s(session_token)

    try:
        await lua_manager.execute("authentication/expire_redis_session", [], [session_token_hash])
    except Exception:
        if emit_on_error:
            logger.warning("expire_redis_session_failed_emitting_event")
            await event_emitter(
                cache,
                "SESSION_EXPIRE_FAILED",
                {"session_token": session_token}
            )
        else:
            logger.warning("expire_redis_session_failed")
            raise
