from uuid import UUID

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.errors.domains.authentication_errors import OtpVerificationError
from server.src.app.errors.domains.core_errors import PendingOrgDeletionNotFoundError
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.store.cache.authentication.verify_otp import verify_otp
from server.src.store.cache.core.pending_organization_deletion import delete_pending_org_deletion, get_pending_org_deletion
from server.src.store.sql.core.organizations.soft_delete_organization import soft_delete_organization

async def complete_organization_deletion(
    pool: Pool,
    cache: Redis,
    user_id: UUID,
    organization_id: UUID,
    otp: str,
) -> None:
    pending = await get_pending_org_deletion(cache, str(user_id), str(organization_id))
    if pending is None:
        raise PendingOrgDeletionNotFoundError()

    if not await verify_otp(cache, pending.email_hash, otp):
        raise OtpVerificationError()

    async with pool.acquire() as conn:
        await soft_delete_organization(conn, organization_id)

    await delete_pending_org_deletion(cache, str(user_id), str(organization_id))

    publisher = RedisEventPublisher(cache)
    await publisher.publish(
        "org_role:invalidation",
        "INVALIDATE_USER_ORG_ROLES",
        {"user_id": str(user_id)},
    )
    await publisher.publish(
        "org_role:invalidation",
        "INVALIDATE_ORG_ALL_ROLES",
        {"organization_id": str(organization_id)},
    )
