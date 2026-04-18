from redis.asyncio import Redis

async def consume_reset_token(cache: Redis, hashed_token: str) -> str | None:
    key = f"reset_token:{hashed_token}"
    email_hash = await cache.getdel(key)
    
    if email_hash is not None:
        return email_hash.decode("utf-8") if isinstance(email_hash, bytes) else email_hash
    return None
