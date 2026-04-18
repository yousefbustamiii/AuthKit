from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.config.email_templates import OrgDeletionTemplate
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.crypto.secrets.generate_otp import generate_otp
from server.src.app.errors.domains.authentication_errors import UserNotFoundError
from server.src.app.errors.domains.core_errors import OrgAccessDeniedError, OrgLastOwnedError
from server.src.app.events.event_emitter import event_emitter
from server.src.store.cache.authentication.store_otp import store_otp
from server.src.store.cache.core.pending_organization_deletion import store_pending_org_deletion
from server.src.store.sql.authentication.users.select_user_by_id import select_user_by_id
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

@dataclass
class InitiateOrgDeletionResult:
    organization_id: str

async def initiate_organization_deletion(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
    country: str,
    device: str,
) -> InitiateOrgDeletionResult:
    membership = await resolve_user_role_in_org(pool, organization_id, user_id, org_role_cache)

    if membership.role != "owner":
        raise OrgAccessDeniedError()

    if membership.owned_org_count <= 1:
        raise OrgLastOwnedError()

    async with pool.acquire() as conn:
        user = await select_user_by_id(conn, user_id)

    if user is None:
        raise UserNotFoundError()

    email = decrypt(user.email_encrypted)
    email_hash = hash_blake2s(email)
    otp = generate_otp()

    await store_pending_org_deletion(cache, str(user_id), str(organization_id), email_hash)
    await store_otp(cache, email_hash, otp)

    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = OrgDeletionTemplate(otp=otp, device=device, country=country, timestamp=timestamp)

    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email,
        "subject": template.subject,
        "message": template.html,
    })

    return InitiateOrgDeletionResult(organization_id=str(organization_id))
