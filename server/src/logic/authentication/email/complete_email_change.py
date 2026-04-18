from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import EmailChangeSuccessTemplate
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.errors.domains.authentication_errors import OtpVerificationError, PendingEmailChangeNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.store.cache.authentication.pending_email_change import delete_pending_email_change, get_pending_email_change
from server.src.store.cache.authentication.verify_otp import verify_otp
from server.src.store.sql.authentication.users.update_user_email import update_user_email

async def complete_email_change(pool: Pool, cache: Redis, user_id: UUID, otp: str, country: str, device: str) -> None:
    pending = await get_pending_email_change(cache, str(user_id))
    if pending is None:
        raise PendingEmailChangeNotFoundError()

    email_hash = hash_blake2s(pending.new_email)

    if not await verify_otp(cache, email_hash, otp):
        raise OtpVerificationError()

    async with pool.acquire() as conn:
        await update_user_email(conn, user_id, pending.new_email)

    await delete_pending_email_change(cache, str(user_id))

    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = EmailChangeSuccessTemplate(device=device, country=country, timestamp=timestamp)
    
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": pending.new_email,
        "subject": template.subject,
        "message": template.html
    })
