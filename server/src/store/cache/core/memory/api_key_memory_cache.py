from cachetools import TTLCache

from server.src.store.cache.core.api_key_redis_cache import ApiKeyCache

def get_memory_api_key(org_api_key_cache: TTLCache, key_hash: str) -> ApiKeyCache | None:
    return org_api_key_cache.get(f"api_key:{key_hash}")

def set_memory_api_key(org_api_key_cache: TTLCache, key_hash: str, api_key: ApiKeyCache) -> None:
    org_api_key_cache[f"api_key:{key_hash}"] = api_key

def delete_memory_api_key(org_api_key_cache: TTLCache, key_hash: str) -> None:
    org_api_key_cache.pop(f"api_key:{key_hash}", None)
