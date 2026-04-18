from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import DeletionTemplate, EmailChangeTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.errors.domains.authentication_errors import NoPendingFlowError
from server.src.app.events.event_emitter import event_emitter
from server.src.store.cache.authentication.pending_deletion import get_pending_deletion
from server.src.store.cache.authentication.pending_email_change import get_pending_email_change
from server.src.store.cache.authentication.refresh_otp import refresh_otp
from server.src.store.sql.authentication.users.select_user_by_id import select_user_by_id

async def resend_otp_authenticated(
    cache: Redis,
    lua_manager: LuaScriptManager,
    pool: Pool,
    user_id: UUID,
    country: str,
    device: str,
) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

    pending_email_change = await get_pending_email_change(cache, str(user_id))
    if pending_email_change is not None:
        new_email = pending_email_change.new_email
        email_hash = hash_blake2s(new_email)
        new_otp = await refresh_otp(cache, lua_manager, email_hash)
        if new_otp is None:
            raise NoPendingFlowError()
        template = EmailChangeTemplate(
            otp=new_otp,
            new_email=new_email,
            device=device,
            country=country,
            timestamp=timestamp,
        )
        await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
            "email": new_email,
            "subject": template.subject,
            "message": template.html,
        })
        return

    pending_deletion = await get_pending_deletion(cache, str(user_id))
    if pending_deletion is not None:
        email_hash = pending_deletion.email_hash
        new_otp = await refresh_otp(cache, lua_manager, email_hash)
        if new_otp is None:
            raise NoPendingFlowError()
        async with pool.acquire() as conn:
            user = await select_user_by_id(conn, user_id)
        email = decrypt(user.email_encrypted)
        template = DeletionTemplate(otp=new_otp, device=device, country=country, timestamp=timestamp)
        await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
            "email": email,
            "subject": template.subject,
            "message": template.html,
        })
        return

    raise NoPendingFlowError()
