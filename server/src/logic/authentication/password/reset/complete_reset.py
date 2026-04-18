from datetime import datetime, timezone

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import PasswordResetSuccessTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.crypto.encryption.argon_hashing import hash_password
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.errors.domains.authentication_errors import InvalidPasswordError, OtpVerificationError, UserNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.app.validation.validate_password import validate_password
from server.src.store.cache.authentication.consume_reset_token import consume_reset_token
from server.src.store.cache.authentication.expire_all_redis_sessions import expire_all_redis_sessions
from server.src.store.sql.authentication.sessions.expire_all_sessions import expire_all_sessions
from server.src.store.sql.authentication.users.select_user_by_email_hash import select_user_by_email_hash
from server.src.store.sql.authentication.users.update_password_hash import update_password_hash

async def complete_password_reset(
    pool: Pool,
    cache: Redis,
    lua_manager: LuaScriptManager,
    reset_token: str,
    new_password: str,
    country: str,
    device: str,
    publisher: RedisEventPublisher,
) -> None:
    is_valid_pass, pass_result = validate_password(new_password)
    if not is_valid_pass:
        raise InvalidPasswordError(pass_result)

    hashed_token = hash_blake2s(reset_token)
    email_hash = await consume_reset_token(cache, hashed_token)
    
    if not email_hash:
        raise OtpVerificationError()

    async with pool.acquire() as conn:
        user = await select_user_by_email_hash(conn, email_hash)
        
    if not user:
        raise UserNotFoundError()

    new_password_hash = await hash_password(new_password)
    
    async with pool.acquire() as conn:
        async with conn.transaction():
            await update_password_hash(conn, user.user_id, new_password_hash)
            await expire_all_sessions(conn, user.user_id)
        
    await expire_all_redis_sessions(cache, lua_manager, user.user_id)

    await publisher.publish(
        "session:invalidation",
        "EXPIRE_USER_SESSIONS_MEMORY",
        {"user_id": str(user.user_id)},
    )

    email = decrypt(user.email_encrypted)
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = PasswordResetSuccessTemplate(device=device, country=country, timestamp=timestamp)
    
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email,
        "subject": template.subject,
        "message": template.html
    })
