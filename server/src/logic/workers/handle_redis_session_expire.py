import asyncio
from uuid import UUID

from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.logging.logger_setup import get_logger
from server.src.store.cache.authentication.expire_all_redis_sessions import expire_all_redis_sessions
from server.src.store.cache.authentication.expire_all_redis_sessions_except import expire_all_redis_sessions_except
from server.src.store.cache.authentication.expire_redis_device_sessions import expire_redis_device_sessions
from server.src.store.cache.authentication.expire_redis_session import expire_redis_session
from server.src.store.cache.authentication.expire_redis_session_by_hash import expire_redis_session_by_hash

logger = get_logger(__name__)

ALL_SESSIONS_RETRIES = [0.1, 0.5, 1.5, 3.0]   # 5.1s total — most dangerous
SINGLE_SESSION_RETRIES = [0.1, 0.5, 1.0]        # 1.6s total — scoped, not catastrophic


async def handle_session_expire(redis: Redis, lua_manager: LuaScriptManager, payload: dict) -> None:
    session_token = payload.get("session_token")
    if not session_token:
        logger.error("missing_session_token", extra={"payload": payload})
        return

    for attempt, delay in enumerate(SINGLE_SESSION_RETRIES, start=1):
        try:
            await expire_redis_session(redis, lua_manager, session_token, emit_on_error=False)
            return
        except Exception:
            logger.warning("handle_session_expire_retry", extra={"attempt": attempt})
            await asyncio.sleep(delay)

    logger.error("handle_session_expire_exhausted")


async def handle_session_hash_expire(redis: Redis, lua_manager: LuaScriptManager, payload: dict) -> None:
    session_token_hash = payload.get("session_token_hash")
    if not session_token_hash:
        logger.error("missing_session_token_hash", extra={"payload": payload})
        return

    for attempt, delay in enumerate(SINGLE_SESSION_RETRIES, start=1):
        try:
            await expire_redis_session_by_hash(redis, lua_manager, session_token_hash, emit_on_error=False)
            return
        except Exception:
            logger.warning("handle_session_hash_expire_retry", extra={"attempt": attempt})
            await asyncio.sleep(delay)

    logger.error("handle_session_hash_expire_exhausted")


async def handle_user_sessions_expire(redis: Redis, lua_manager: LuaScriptManager, payload: dict) -> None:
    user_id_str = payload.get("user_id")
    if not user_id_str:
        logger.error("missing_user_id", extra={"payload": payload})
        return

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        logger.error("invalid_user_id", extra={"payload": payload})
        return

    for attempt, delay in enumerate(ALL_SESSIONS_RETRIES, start=1):
        try:
            await expire_all_redis_sessions(redis, lua_manager, user_id, emit_on_error=False)
            return
        except Exception:
            logger.warning("handle_user_sessions_expire_retry", extra={"user_id": user_id_str, "attempt": attempt})
            await asyncio.sleep(delay)

    logger.error("handle_user_sessions_expire_exhausted", extra={"user_id": user_id_str})


async def handle_device_sessions_expire(redis: Redis, lua_manager: LuaScriptManager, payload: dict) -> None:
    device_ids_str = payload.get("device_ids", [])
    if not device_ids_str:
        logger.error("missing_device_ids", extra={"payload": payload})
        return

    try:
        device_ids = [UUID(did) for did in device_ids_str]
    except ValueError:
        logger.error("invalid_device_ids", extra={"payload": payload})
        return

    for attempt, delay in enumerate(SINGLE_SESSION_RETRIES, start=1):
        try:
            await expire_redis_device_sessions(redis, lua_manager, device_ids, emit_on_error=False)
            return
        except Exception:
            logger.warning("handle_device_sessions_expire_retry", extra={"attempt": attempt})
            await asyncio.sleep(delay)

    logger.error("handle_device_sessions_expire_exhausted")


async def handle_user_sessions_expire_except(redis: Redis, lua_manager: LuaScriptManager, payload: dict) -> None:
    user_id_str = payload.get("user_id")
    session_token_hash = payload.get("session_token_hash")
    if not user_id_str or not session_token_hash:
        logger.error("missing_user_id_or_session_token_hash", extra={"payload": payload})
        return

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        logger.error("invalid_user_id", extra={"payload": payload})
        return

    for attempt, delay in enumerate(ALL_SESSIONS_RETRIES, start=1):
        try:
            await expire_all_redis_sessions_except(redis, lua_manager, user_id, session_token_hash)
            return
        except Exception:
            logger.warning("handle_user_sessions_expire_except_retry", extra={"user_id": user_id_str, "attempt": attempt})
            await asyncio.sleep(delay)

    logger.error("handle_user_sessions_expire_except_exhausted", extra={"user_id": user_id_str})
