from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import EmailChangeTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.crypto.secrets.generate_otp import generate_otp
from server.src.app.errors.domains.authentication_errors import InvalidEmailError, OAuthProviderActionNotAllowedError, UserNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.validation.validate_email import validate_email
from server.src.store.cache.authentication.pending_email_change import store_pending_email_change
from server.src.store.cache.authentication.store_otp import store_otp
from server.src.store.sql.authentication.users.select_user_by_id import select_user_by_id

@dataclass
class InitiateEmailChangeResult:
    user_id: str

async def initiate_email_change(pool: Pool, cache: Redis, lua_manager: LuaScriptManager, user_id: UUID, new_email: str, country: str, device: str) -> InitiateEmailChangeResult:
    async with pool.acquire() as conn:
        user = await select_user_by_id(conn, user_id)
    if user is None:
        raise UserNotFoundError()
    if user.provider != "email":
        raise OAuthProviderActionNotAllowedError()

    is_valid_email, email_result = validate_email(new_email)
    if not is_valid_email:
        raise InvalidEmailError(email_result)
    normalized_email = email_result

    email_hash = hash_blake2s(normalized_email)
    otp = generate_otp()

    await store_pending_email_change(cache, lua_manager, str(user_id), normalized_email)
    await store_otp(cache, email_hash, otp)
    
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = EmailChangeTemplate(otp=otp, new_email=normalized_email, device=device, country=country, timestamp=timestamp)
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": normalized_email, 
        "subject": template.subject, 
        "message": template.html
    })

    return InitiateEmailChangeResult(user_id=str(user_id))
