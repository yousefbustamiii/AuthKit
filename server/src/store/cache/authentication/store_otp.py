from redis.asyncio import Redis

from server.src.app.config.settings import settings
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

async def store_otp(cache: Redis, email_hash: str, otp: str) -> None:
    key = f"otp:{email_hash}"
    otp_hash = hash_blake2s(otp)
    await cache.setex(key, settings.otp.expire_minutes * 60, otp_hash)
