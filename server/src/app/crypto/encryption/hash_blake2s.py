import hashlib

from server.src.app.config.settings import settings

def hash_blake2s(data: str | bytes, digest_size: int = 32) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.blake2s(
        data, 
        digest_size=digest_size, 
        key=settings.blake2s_hashing_key
    ).hexdigest()
