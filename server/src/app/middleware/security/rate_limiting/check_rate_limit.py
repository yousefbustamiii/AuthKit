from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.store.cache.authentication.memory.rate_limit_memory_cache import get_blocked_key, set_blocked_key

async def check_rate_limit(
    cache: Redis,
    lua_manager: LuaScriptManager,
    limits: list[tuple[str, int, int]],
    rate_limit_cache: TTLCache | None = None,
) -> tuple[bool, int, str]:
    if not limits:
        return True, 0, ""

    # L1: memory — short-circuit if any key is already known to be blocked
    if rate_limit_cache is not None:
        for key, _, _ in limits:
            remaining = get_blocked_key(rate_limit_cache, key)
            if remaining is not None:
                return False, remaining, key

    keys = []
    args = []

    for key, max_hits, window in limits:
        if max_hits <= 0 or window <= 0:
            raise ValueError("max_hits and window must be positive")
        keys.append(key)
        args.extend([max_hits, window])

    result = await lua_manager.execute("shared/token_bucket", keys, args)
    allowed, retry_after_sec, exhausted_key = result[0] == 1, result[1], result[2]

    # L1 hydration — cache the blocked key so future requests skip Redis
    if not allowed and rate_limit_cache is not None:
        set_blocked_key(rate_limit_cache, exhausted_key, retry_after_sec)

    return allowed, retry_after_sec, exhausted_key
