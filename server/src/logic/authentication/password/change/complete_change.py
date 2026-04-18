from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import PasswordChangeSuccessTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.crypto.encryption.argon_hashing import hash_password, verify_password_hash
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.errors.domains.authentication_errors import IncorrectPasswordError, InvalidPasswordError, OAuthProviderActionNotAllowedError, SamePasswordError, UserNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.app.validation.validate_password import validate_password
from server.src.store.cache.authentication.expire_all_redis_sessions_except import expire_all_redis_sessions_except
from server.src.store.sql.authentication.sessions.expire_all_sessions_except import expire_all_sessions_except
from server.src.store.sql.authentication.users.select_user_by_id import select_user_by_id
from server.src.store.sql.authentication.users.update_password_hash import update_password_hash

async def complete_password_change(
    pool: Pool,
    cache: Redis,
    lua_manager: LuaScriptManager,
    user_id: UUID,
    old_password: str,
    new_password: str,
    country: str,
    device: str,
    session_token: str,
    publisher: RedisEventPublisher,
) -> None:
    if not old_password:
        raise InvalidPasswordError("Old password cannot be empty")

    is_valid_new, new_res = validate_password(new_password)
    if not is_valid_new:
        raise InvalidPasswordError(f"New password: {new_res}")

    if old_password == new_password:
        raise SamePasswordError()

    async with pool.acquire() as conn:
        user = await select_user_by_id(conn, user_id)
    if user is None:
        raise UserNotFoundError()
    if user.provider != "email":
        raise OAuthProviderActionNotAllowedError()
    if user.password_hash is None:
        raise IncorrectPasswordError()

    is_valid = await verify_password_hash(user.password_hash, old_password)
    if not is_valid:
        raise IncorrectPasswordError()

    new_password_hash = await hash_password(new_password)
    
    async with pool.acquire() as conn:
        async with conn.transaction():
            await update_password_hash(conn, user_id, new_password_hash)
            await expire_all_sessions_except(conn, user_id, session_token)
    session_token_hash = hash_blake2s(session_token)
    await expire_all_redis_sessions_except(cache, lua_manager, user_id, session_token_hash)

    await publisher.publish(
        "session:invalidation",
        "EXPIRE_USER_SESSIONS_EXCEPT_MEMORY",
        {"user_id": str(user_id), "session_token_hash": session_token_hash},
    )

    email = decrypt(user.email_encrypted)
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = PasswordChangeSuccessTemplate(device=device, country=country, timestamp=timestamp)
    
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email,
        "subject": template.subject,
        "message": template.html
    })
