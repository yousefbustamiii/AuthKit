from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.config.email_templates import OrgDeletionTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.errors.domains.authentication_errors import NoPendingFlowError, UserNotFoundError
from server.src.app.errors.domains.core_errors import OrgAccessDeniedError, PendingOrgDeletionNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.store.cache.authentication.refresh_otp import refresh_otp
from server.src.store.cache.core.pending_organization_deletion import get_pending_org_deletion
from server.src.store.sql.authentication.users.select_user_by_id import select_user_by_id
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

async def resend_organization_deletion(
    pool: Pool,
    cache: Redis,
    lua_manager: LuaScriptManager,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
    country: str,
    device: str,
) -> None:
    membership = await resolve_user_role_in_org(pool, organization_id, user_id, org_role_cache)
    if membership.role != "owner":
        raise OrgAccessDeniedError()

    pending = await get_pending_org_deletion(cache, str(user_id), str(organization_id))
    if pending is None:
        raise PendingOrgDeletionNotFoundError()

    new_otp = await refresh_otp(cache, lua_manager, pending.email_hash)
    if new_otp is None:
        raise NoPendingFlowError()

    async with pool.acquire() as conn:
        user = await select_user_by_id(conn, user_id)

    if user is None:
        raise UserNotFoundError()

    email = decrypt(user.email_encrypted)
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = OrgDeletionTemplate(otp=new_otp, device=device, country=country, timestamp=timestamp)

    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email,
        "subject": template.subject,
        "message": template.html,
    })
