from dataclasses import dataclass
from datetime import datetime, timezone

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import SignupTemplate
from server.src.app.crypto.encryption.argon_hashing import hash_password
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.crypto.secrets.generate_otp import generate_otp
from server.src.app.errors.domains.authentication_errors import EmailAlreadyTakenError, InvalidEmailError, InvalidPasswordError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.validation.validate_email import validate_email
from server.src.app.validation.validate_password import validate_password
from server.src.store.cache.authentication.pending_signup import store_pending_signup
from server.src.store.cache.authentication.store_otp import store_otp
from server.src.store.sql.authentication.users.select_user_by_email_hash import select_user_by_email_hash

@dataclass
class InitiateSignupResult:
    email_hash: str

async def initiate_signup(pool: Pool, cache: Redis, email: str, password: str, country: str, device: str, name: str | None = None) -> InitiateSignupResult:
    is_valid_email, email_result = validate_email(email)
    if not is_valid_email:
        raise InvalidEmailError(email_result)
    normalized_email = email_result

    is_valid_pass, pass_result = validate_password(password)
    if not is_valid_pass:
        raise InvalidPasswordError(pass_result)

    email_hash = hash_blake2s(normalized_email)

    async with pool.acquire() as conn:
        existing_user = await select_user_by_email_hash(conn, email_hash)
        if existing_user:
            raise EmailAlreadyTakenError()

    password_hash = await hash_password(password)
    otp = generate_otp()

    await store_pending_signup(cache, email_hash, normalized_email, password_hash, name)
    await store_otp(cache, email_hash, otp)
    
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = SignupTemplate(otp=otp, device=device, country=country, timestamp=timestamp)
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": normalized_email, 
        "subject": template.subject, 
        "message": template.html
    })

    return InitiateSignupResult(email_hash=email_hash)
