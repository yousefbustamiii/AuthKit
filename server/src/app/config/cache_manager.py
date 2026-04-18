from cachetools import TTLCache

def create_memory_cache(maxsize: int = 10_000, ttl: int = 60) -> TTLCache:
    return TTLCache(maxsize=maxsize, ttl=ttl)
