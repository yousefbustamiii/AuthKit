from redis.asyncio import Redis

async def store_dummy_otp(cache: Redis, email_hash: str, otp: str) -> None:
    key = f"dummy_otp:{email_hash}"
    await cache.setex(key, 10, otp)
