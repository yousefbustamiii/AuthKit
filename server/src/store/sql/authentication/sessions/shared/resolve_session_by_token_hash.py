from datetime import datetime
from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.logging.logger_setup import get_logger
from server.src.store.cache.authentication.memory.session_memory_cache import get_memory_session, set_memory_session
from server.src.store.cache.authentication.set_redis_session import set_redis_session
from server.src.store.sql.authentication.sessions.select_session_by_token_hash import SessionByTokenHash, select_session_by_token_hash

logger = get_logger(__name__)

async def resolve_session_by_token_hash(
    cache: Redis,
    pool: Pool,
    session_token: str,
    session_cache: TTLCache,
    lua_manager: LuaScriptManager,
) -> SessionByTokenHash | None:
    session_token_hash = hash_blake2s(session_token)

    # L1: per-worker session cache
    session = get_memory_session(session_cache, session_token_hash)
    if session is not None:
        return session

    # L2: Redis
    session_key = f"session:{session_token_hash}"
    try:
        data = await cache.hgetall(session_key)
        if data:
            session = SessionByTokenHash(
                session_id=UUID(data["session_id"]),
                user_id=UUID(data["user_id"]),
                expires_at=datetime.fromisoformat(data["expires_at"]),
                account_status=data["account_status"],
                device_id=UUID(data["device_id"]) if data.get("device_id") else None,
            )
            set_memory_session(session_cache, session_token_hash, session)
            return session
    except Exception:
        logger.warning("resolve_session_redis_fallback")

    # L3: PostgreSQL
    async with pool.acquire() as conn:
        session = await select_session_by_token_hash(conn, session_token)

    if session is None:
        return None

    await set_redis_session(
        cache,
        lua_manager,
        session_token,
        session.session_id,
        session.user_id,
        session.expires_at,
        account_status=session.account_status,
        device_id=session.device_id,
    )
    set_memory_session(session_cache, session_token_hash, session)

    return session
