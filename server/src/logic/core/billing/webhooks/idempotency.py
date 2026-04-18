from redis.asyncio import Redis

TTL_SECONDS = 86400 * 7  # 7 days

async def try_claim_event(cache: Redis, event_id: str) -> bool:
    result = await cache.set(f"stripe:event:{event_id}", "1", nx=True, ex=TTL_SECONDS)
    return result is not None

async def release_event_claim(cache: Redis, event_id: str) -> None:
    await cache.delete(f"stripe:event:{event_id}")
