from dataclasses import dataclass

from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

@dataclass
class IdempotencyResult:
    is_new: bool
    stored_hash: str | None

async def check_and_set_idempotency(cache: Redis, lua_manager: LuaScriptManager, key: str, payload_hash: str) -> IdempotencyResult:
    redis_key = f"idempotency:{key}"
    
    result = await lua_manager.execute("idempotency", [redis_key], [payload_hash])
    
    if result == 0:
        return IdempotencyResult(is_new=True, stored_hash=None)
    
    return IdempotencyResult(is_new=False, stored_hash=result)

async def delete_idempotency_key(cache: Redis, key: str) -> None:
    redis_key = f"idempotency:{key}"
    await cache.delete(redis_key)

def hash_payload(payload: bytes) -> str:
    return hash_blake2s(payload)