from dataclasses import dataclass
from uuid import UUID

from redis.asyncio import Redis

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

REDIS_TTL_SECONDS = 86400  # 24 hours

@dataclass
class ApiKeyCache:
    key_id: UUID
    project_id: UUID
    org_id: UUID
    plan: str
    status: str | None

async def get_redis_api_key(cache: Redis, key_hash: str) -> ApiKeyCache | None:
    key = f"api_key:{key_hash}"
    try:
        data = await cache.hgetall(key)
        if not data:
            return None

        return ApiKeyCache(
            key_id=UUID(data["key_id"]),
            project_id=UUID(data["project_id"]),
            org_id=UUID(data["org_id"]),
            plan=data["plan"],
            status=data["status"] if data["status"] else None,
        )
    except Exception as e:
        logger.warning("get_redis_api_key_failed", extra={"error": str(e), "key_hash": hash_blake2s(key_hash, digest_size=5)})
        return None


async def set_redis_api_key(
    cache: Redis,
    key_hash: str,
    key_id: UUID,
    project_id: UUID,
    org_id: UUID,
    plan: str,
    status: str | None,
) -> None:
    key = f"api_key:{key_hash}"
    try:
        mapping = {
            "key_id": str(key_id),
            "project_id": str(project_id),
            "org_id": str(org_id),
            "plan": plan,
            "status": status if status else "",
        }
        async with cache.pipeline() as pipe:
            pipe.hset(key, mapping=mapping)
            pipe.expire(key, REDIS_TTL_SECONDS)
            await pipe.execute()
    except Exception as e:
        logger.warning("set_redis_api_key_failed", extra={"error": str(e), "key_hash": hash_blake2s(key_hash, digest_size=5)})


async def delete_redis_api_key(cache: Redis, key_hash: str) -> None:
    key = f"api_key:{key_hash}"
    try:
        await cache.delete(key)
    except Exception as e:
        logger.warning("delete_redis_api_key_failed", extra={"error": str(e), "key_hash": hash_blake2s(key_hash, digest_size=5)})
