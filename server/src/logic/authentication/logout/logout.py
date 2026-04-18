from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.app.logging.logger_setup import get_logger
from server.src.store.cache.authentication.expire_redis_session import expire_redis_session
from server.src.store.sql.authentication.sessions.expire_session import expire_session

logger = get_logger(__name__)

async def logout(pool: Pool, cache: Redis, lua_manager: LuaScriptManager, session_token: str, publisher: RedisEventPublisher) -> None:
    async with pool.acquire() as conn:
        await expire_session(conn, session_token)

    await expire_redis_session(cache, lua_manager, session_token)

    await publisher.publish(
        "session:invalidation",
        "EXPIRE_SINGLE_SESSION_MEMORY",
        {"session_token_hash": hash_blake2s(session_token)},
    )
