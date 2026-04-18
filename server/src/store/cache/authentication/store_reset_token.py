from redis.asyncio import Redis

async def store_reset_token(cache: Redis, hashed_token: str, email_hash: str) -> None:
    key = f"reset_token:{hashed_token}"
    await cache.setex(key, 900, email_hash)
