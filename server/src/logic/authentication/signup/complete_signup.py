from dataclasses import dataclass
from datetime import datetime, timezone

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import NewLoginTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.errors.domains.authentication_errors import OtpVerificationError, PendingSignupNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.logic.authentication.shared.bootstrap_new_user import bootstrap_new_user
from server.src.store.cache.authentication.expire_redis_session_by_hash import expire_redis_session_by_hash
from server.src.store.cache.authentication.pending_signup import delete_pending_signup, get_pending_signup
from server.src.store.cache.authentication.set_redis_session import set_redis_session
from server.src.store.cache.authentication.verify_otp import verify_otp

@dataclass
class CompleteSignupResult:
    session_token: str
    device_token: str
    expires_at: datetime

async def complete_signup(
    pool: Pool,
    cache: Redis,
    lua_manager: LuaScriptManager,
    email_hash: str,
    otp: str,
    country: str,
    device: str,
    publisher: RedisEventPublisher,
) -> CompleteSignupResult:
    pending = await get_pending_signup(cache, email_hash)
    if pending is None:
        raise PendingSignupNotFoundError()

    if not await verify_otp(cache, email_hash, otp):
        raise OtpVerificationError()

    async with pool.acquire() as conn:
        async with conn.transaction():
            bootstrap = await bootstrap_new_user(
                conn,
                email=pending.email,
                provider="email",
                password_hash=pending.password_hash,
                name=pending.name,
                country=country,
                device=device,
            )
            session = bootstrap.session

    await set_redis_session(
        cache,
        lua_manager,
        session.session_token,
        session.session_id,
        bootstrap.user_id,
        session.expires_at,
        device_id=session.device_id,
    )
    if session.killed_session_token_hash:
        await expire_redis_session_by_hash(cache, lua_manager, session.killed_session_token_hash)
        await publisher.publish(
            "session:invalidation",
            "EXPIRE_SINGLE_SESSION_MEMORY",
            {"session_token_hash": session.killed_session_token_hash},
        )

    await delete_pending_signup(cache, email_hash)

    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = NewLoginTemplate(device=device, country=country, timestamp=timestamp)

    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": pending.email,
        "subject": template.subject,
        "message": template.html
    })

    return CompleteSignupResult(
        session_token=session.session_token,
        device_token=session.device_token,
        expires_at=session.expires_at
    )
