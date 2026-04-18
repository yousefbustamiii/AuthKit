from dataclasses import dataclass
from uuid import UUID

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.store.cache.authentication.expire_redis_device_sessions import expire_redis_device_sessions
from server.src.store.sql.authentication.devices.soft_delete_devices import soft_delete_devices

@dataclass
class DeviceDeletionResult:
    deleted_count: int


async def delete_devices(
    pool: Pool,
    cache: Redis,
    lua_manager: LuaScriptManager,
    user_id: UUID,
    device_ids: list[UUID],
    publisher: RedisEventPublisher,
) -> DeviceDeletionResult:
    async with pool.acquire() as conn:
        deleted_count = await soft_delete_devices(conn, user_id, device_ids)

    await expire_redis_device_sessions(cache, lua_manager, device_ids)

    await publisher.publish(
        "session:invalidation",
        "EXPIRE_DEVICE_SESSIONS_MEMORY",
        {"device_ids": [str(d) for d in device_ids]},
    )

    return DeviceDeletionResult(deleted_count=deleted_count)
