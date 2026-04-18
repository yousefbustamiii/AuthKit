import secrets

from redis.asyncio import Redis

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.errors.domains.authentication_errors import InvalidEmailError, OtpVerificationError
from server.src.app.validation.validate_email import validate_email
from server.src.store.cache.authentication.store_reset_token import store_reset_token
from server.src.store.cache.authentication.verify_otp import verify_otp

async def verify_password_reset_otp(cache: Redis, email: str, otp: str) -> str:
    is_valid_email, email_result = validate_email(email)
    if not is_valid_email:
        raise InvalidEmailError(email_result)

    email_hash = hash_blake2s(email_result)
    is_valid_otp = await verify_otp(cache, email_hash, otp)
    
    if not is_valid_otp:
        raise OtpVerificationError()

    # Generate a secure 32-byte URL-safe string token
    reset_token = secrets.token_urlsafe(32)
    hashed_token = hash_blake2s(reset_token)

    # Store the hashed token -> email_hash mapping
    await store_reset_token(cache, hashed_token, email_hash)

    return reset_token
