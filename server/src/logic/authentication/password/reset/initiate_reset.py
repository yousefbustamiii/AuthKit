from datetime import datetime, timezone

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import DummyTemplate, PasswordResetTemplate
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.crypto.secrets.generate_otp import generate_otp
from server.src.app.errors.domains.authentication_errors import InvalidEmailError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.validation.validate_email import validate_email
from server.src.store.cache.authentication.dummy_otp import store_dummy_otp
from server.src.store.cache.authentication.store_otp import store_otp
from server.src.store.sql.authentication.users.select_user_by_email_hash import select_user_by_email_hash

async def initiate_password_reset(pool: Pool, cache: Redis, email: str, country: str, device: str) -> None:
    is_valid_email, email_result = validate_email(email)
    if not is_valid_email:
        raise InvalidEmailError(email_result)
    email_hash = hash_blake2s(email_result)

    async with pool.acquire() as conn:
        user = await select_user_by_email_hash(conn, email_hash)

    if user:
        otp = generate_otp()
        await store_otp(cache, email_hash, otp)
        
        timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
        template = PasswordResetTemplate(otp=otp, device=device, country=country, timestamp=timestamp)
        await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
            "email": email_result, 
            "subject": template.subject, 
            "message": template.html
        })
    else:
        otp = generate_otp()
        await store_dummy_otp(cache, email_hash, otp)
        
        template = DummyTemplate()
        await event_emitter(cache, "DUMMY_EMAIL", {
            "email": email_result, 
            "message": template.html
        })
