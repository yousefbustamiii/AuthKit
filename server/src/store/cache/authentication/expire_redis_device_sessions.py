from uuid import UUID

from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.events.event_emitter import event_emitter
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

async def expire_redis_device_sessions(cache: Redis, lua_manager: LuaScriptManager, device_ids: list[UUID], emit_on_error: bool = True) -> None:
    device_keys = [f"device_sessions:{did}" for did in device_ids]

    num_keys = len(device_keys)

    try:
        await lua_manager.execute("authentication/expire_redis_device_sessions", device_keys, [])
    except Exception:
        if emit_on_error:
            logger.warning("expire_redis_device_sessions_failed_emitting_event")
            await event_emitter(
                cache,
                "DEVICE_SESSIONS_EXPIRE_FAILED",
                {"device_ids": [str(d) for d in device_ids]}
            )
        else:
            logger.warning("expire_redis_device_sessions_failed")
            raise
