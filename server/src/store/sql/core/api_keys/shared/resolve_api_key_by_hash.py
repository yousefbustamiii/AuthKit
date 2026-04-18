from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.store.cache.core.api_key_redis_cache import ApiKeyCache, get_redis_api_key, set_redis_api_key
from server.src.store.cache.core.memory.api_key_memory_cache import get_memory_api_key, set_memory_api_key
from server.src.store.sql.core.api_keys.select_api_key_by_hash import select_api_key_by_hash

async def resolve_api_key_by_hash(
    cache: Redis,
    pool: Pool,
    key_hash: str,
    org_api_key_cache: TTLCache,
) -> ApiKeyCache | None:
    
    # L1: In-Memory TTL Cache Check
    memory_key = get_memory_api_key(org_api_key_cache, key_hash)
    if memory_key is not None:
        return memory_key

    # L2: Redis Cache Check
    redis_key = await get_redis_api_key(cache, key_hash)
    if redis_key is not None:
        # Hydrate L1
        set_memory_api_key(org_api_key_cache, key_hash, redis_key)
        return redis_key

    # L3: PostgreSQL Database Check
    async with pool.acquire() as conn:
        db_key = await select_api_key_by_hash(conn, key_hash)

    if db_key is None:
        return None

    cached = ApiKeyCache(
        key_id=db_key.key_id,
        project_id=db_key.project_id,
        org_id=db_key.organization_id,
        plan=db_key.plan,
        status=db_key.status,
    )

    # Hydrate both L2 (Redis) and L1 (Memory) sequentialy
    await set_redis_api_key(cache, key_hash, cached.key_id, cached.project_id, cached.org_id, cached.plan, cached.status)
    set_memory_api_key(org_api_key_cache, key_hash, cached)

    return cached
