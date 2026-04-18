from dataclasses import dataclass

import orjson
from redis.asyncio import Redis

from server.src.app.config.settings import settings

@dataclass
class PendingSignup:
    email_hash: str
    email: str
    password_hash: str
    name: str | None

async def store_pending_signup(cache: Redis, email_hash: str, email: str, password_hash: str, name: str | None = None) -> None:
    key = f"pending_signup:{email_hash}"
    data = orjson.dumps({"email": email, "password_hash": password_hash, "name": name}).decode()
    await cache.setex(key, settings.otp.expire_minutes * 60, data)

async def get_pending_signup(cache: Redis, email_hash: str) -> PendingSignup | None:
    key = f"pending_signup:{email_hash}"
    value = await cache.get(key)
    if value is None:
        return None
    data = orjson.loads(value)
    return PendingSignup(
        email_hash=email_hash,
        email=data["email"],
        password_hash=data["password_hash"],
        name=data.get("name"),
    )

async def delete_pending_signup(cache: Redis, email_hash: str) -> None:
    key = f"pending_signup:{email_hash}"
    await cache.delete(key)
