from dataclasses import dataclass
from datetime import datetime, timezone

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import NewLoginTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.errors.domains.authentication_errors import OtpVerificationError, UserNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.logic.authentication.shared.issue_session_with_device import issue_session_with_device
from server.src.store.cache.authentication.expire_redis_session_by_hash import expire_redis_session_by_hash
from server.src.store.cache.authentication.set_redis_session import set_redis_session
from server.src.store.cache.authentication.verify_otp import verify_otp
from server.src.store.sql.authentication.users.select_user_by_email_hash import select_user_by_email_hash

@dataclass
class CompleteLoginResult:
    session_token: str
    device_token: str
    expires_at: datetime

async def complete_login(
    pool: Pool,
    cache: Redis,
    lua_manager: LuaScriptManager,
    email_hash: str,
    otp: str,
    country: str,
    device: str,
    publisher: RedisEventPublisher,
) -> CompleteLoginResult:
    if not await verify_otp(cache, email_hash, otp):
        raise OtpVerificationError()

    async with pool.acquire() as conn:
        user = await select_user_by_email_hash(conn, email_hash)
        if user is None:
            raise UserNotFoundError()

        async with conn.transaction():
            session = await issue_session_with_device(conn, user.user_id, country, device)
    await set_redis_session(cache, lua_manager, session.session_token, session.session_id, user.user_id, session.expires_at, device_id=session.device_id)
    if session.killed_session_token_hash:
        await expire_redis_session_by_hash(cache, lua_manager, session.killed_session_token_hash)
        await publisher.publish(
            "session:invalidation",
            "EXPIRE_SINGLE_SESSION_MEMORY",
            {"session_token_hash": session.killed_session_token_hash},
        )

    email = decrypt(user.email_encrypted)
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = NewLoginTemplate(device=device, country=country, timestamp=timestamp)

    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email,
        "subject": template.subject,
        "message": template.html
    })

    return CompleteLoginResult(
        session_token=session.session_token,
        device_token=session.device_token,
        expires_at=session.expires_at
    )
