from datetime import datetime, timezone

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import LoginTemplate, PasswordResetTemplate, SignupTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.errors.domains.authentication_errors import InvalidEmailError, NoPendingFlowError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.validation.validate_email import validate_email
from server.src.store.cache.authentication.pending_signup import get_pending_signup
from server.src.store.cache.authentication.refresh_otp import refresh_otp
from server.src.store.cache.authentication.store_otp import store_otp
from server.src.app.crypto.secrets.generate_otp import generate_otp
from server.src.store.sql.authentication.users.select_user_by_email_hash import select_user_by_email_hash

async def resend_otp_public(
    cache: Redis,
    lua_manager: LuaScriptManager,
    pool: Pool,
    email: str,
    email_hash: str,
    country: str,
    device: str,
) -> None:
    is_valid_email, email_result = validate_email(email)
    if not is_valid_email:
        raise InvalidEmailError(email_result)
    normalized_email = email_result

    derived_hash = hash_blake2s(normalized_email)
    if derived_hash != email_hash:
        raise InvalidEmailError("Email checksum invalid")

    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

    pending_signup = await get_pending_signup(cache, email_hash)
    if pending_signup is not None:
        new_otp = await refresh_otp(cache, lua_manager, email_hash)
        if new_otp is None:
            new_otp = generate_otp()
            await store_otp(cache, email_hash, new_otp)
        template = SignupTemplate(otp=new_otp, device=device, country=country, timestamp=timestamp)
        await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
            "email": normalized_email,
            "subject": template.subject,
            "message": template.html,
        })
        return

    new_otp = await refresh_otp(cache, lua_manager, email_hash)
    if new_otp is None:
        raise NoPendingFlowError()

    async with pool.acquire() as conn:
        user = await select_user_by_email_hash(conn, email_hash)

    if user is not None:
        registered_email = decrypt(user.email_encrypted)
        template = LoginTemplate(otp=new_otp, device=device, country=country, timestamp=timestamp)
        await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
            "email": registered_email,
            "subject": template.subject,
            "message": template.html,
        })
    else:
        template = PasswordResetTemplate(otp=new_otp, device=device, country=country, timestamp=timestamp)
        await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
            "email": normalized_email,
            "subject": template.subject,
            "message": template.html,
        })
