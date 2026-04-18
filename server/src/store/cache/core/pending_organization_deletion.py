from dataclasses import dataclass

from redis.asyncio import Redis

from server.src.app.config.settings import settings

@dataclass
class PendingOrganizationDeletion:
    user_id: str
    organization_id: str
    email_hash: str

async def store_pending_org_deletion(cache: Redis, user_id: str, organization_id: str, email_hash: str) -> None:
    key = f"pending_org_deletion:{user_id}:{organization_id}"
    ttl = settings.otp.expire_minutes * 60
    await cache.setex(key, ttl, email_hash)

async def get_pending_org_deletion(cache: Redis, user_id: str, organization_id: str) -> PendingOrganizationDeletion | None:
    key = f"pending_org_deletion:{user_id}:{organization_id}"
    email_hash = await cache.get(key)
    if email_hash is None:
        return None
    if isinstance(email_hash, bytes):
        email_hash = email_hash.decode("utf-8")
    return PendingOrganizationDeletion(user_id=user_id, organization_id=organization_id, email_hash=email_hash)

async def delete_pending_org_deletion(cache: Redis, user_id: str, organization_id: str) -> None:
    key = f"pending_org_deletion:{user_id}:{organization_id}"
    await cache.delete(key)
