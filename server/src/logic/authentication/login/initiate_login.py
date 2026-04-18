from dataclasses import dataclass
from datetime import datetime, timezone

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import LoginTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.argon_hashing import verify_password_hash
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.crypto.secrets.generate_otp import generate_otp
from server.src.app.errors.domains.authentication_errors import IncorrectPasswordError, InvalidEmailError, UserNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.app.validation.validate_email import validate_email
from server.src.logic.authentication.shared.issue_session import issue_session
from server.src.store.cache.authentication.expire_redis_session_by_hash import expire_redis_session_by_hash
from server.src.store.cache.authentication.set_redis_session import set_redis_session
from server.src.store.cache.authentication.store_otp import store_otp
from server.src.store.sql.authentication.devices.select_device_by_token_hash import select_device_by_token_hash
from server.src.store.sql.authentication.users.select_user_by_email_hash import select_user_by_email_hash

@dataclass
class InitiateLoginResult:
    session_token: str | None = None
    expires_at: datetime | None = None
    email_hash: str | None = None
    clear_device_cookie: bool = False

async def initiate_login(
    pool: Pool,
    cache: Redis,
    lua_manager: LuaScriptManager,
    email: str,
    password: str,
    country: str,
    device: str,
    publisher: RedisEventPublisher,
    device_token: str | None = None,
) -> InitiateLoginResult:
    is_valid_email, email_result = validate_email(email)
    if not is_valid_email:
        raise InvalidEmailError(email_result)
    normalized_email = email_result

    email_hash = hash_blake2s(normalized_email)

    async with pool.acquire() as conn:
        user = await select_user_by_email_hash(conn, email_hash)

    if user is None:
        raise UserNotFoundError()

    is_valid_password = await verify_password_hash(user.password_hash, password)
    if not is_valid_password:
        raise IncorrectPasswordError()

    if device_token:
        async with pool.acquire() as conn:
            trusted = await select_device_by_token_hash(conn, user.user_id, device_token)

            if trusted is not None:
                async with conn.transaction():
                    session = await issue_session(conn, user.user_id, country, device, device_id=trusted.device_id)
                await set_redis_session(cache, lua_manager, session.session_token, session.session_id, user.user_id, session.expires_at, device_id=session.device_id)
                if session.killed_session_token_hash:
                    await expire_redis_session_by_hash(cache, lua_manager, session.killed_session_token_hash)
                    await publisher.publish(
                        "session:invalidation",
                        "EXPIRE_SINGLE_SESSION_MEMORY",
                        {"session_token_hash": session.killed_session_token_hash},
                    )
                return InitiateLoginResult(
                    session_token=session.session_token,
                    expires_at=session.expires_at
                )

        otp = generate_otp()
        await store_otp(cache, email_hash, otp)

        timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
        template = LoginTemplate(otp=otp, device=device, country=country, timestamp=timestamp)
        await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
            "email": normalized_email,
            "subject": template.subject,
            "message": template.html
        })

        return InitiateLoginResult(email_hash=email_hash, clear_device_cookie=True)

    otp = generate_otp()
    await store_otp(cache, email_hash, otp)

    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = LoginTemplate(otp=otp, device=device, country=country, timestamp=timestamp)
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": normalized_email,
        "subject": template.subject,
        "message": template.html
    })

    return InitiateLoginResult(email_hash=email_hash)
