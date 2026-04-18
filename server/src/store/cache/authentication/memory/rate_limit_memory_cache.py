import math
import time

from cachetools import TTLCache

def get_blocked_key(rate_limit_cache: TTLCache, key: str) -> int | None:
    entry = rate_limit_cache.get(key)
    if entry is None:
        return None
    remaining = entry - time.monotonic()
    if remaining <= 0:
        return None
    return math.ceil(remaining)

def set_blocked_key(rate_limit_cache: TTLCache, key: str, retry_after_s: int) -> None:
    rate_limit_cache[key] = time.monotonic() + retry_after_s
