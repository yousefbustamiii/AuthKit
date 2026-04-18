import hmac

from redis.asyncio import Redis

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

async def verify_otp(cache: Redis, email_hash: str, otp: str) -> bool:
    key = f"otp:{email_hash}"
    stored_hash = await cache.getdel(key)
    if stored_hash is None:
        return False
    
    if isinstance(stored_hash, bytes):
        stored_hash = stored_hash.decode("utf-8")

    otp_hash = hash_blake2s(otp)
    if not hmac.compare_digest(stored_hash, otp_hash):
        return False
    return True
