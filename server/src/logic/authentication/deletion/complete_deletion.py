from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import AccountDeletionSuccessTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.errors.domains.authentication_errors import OtpVerificationError, PendingUserDeletionNotFoundError, UserNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.store.cache.authentication.expire_all_redis_sessions import expire_all_redis_sessions
from server.src.store.cache.authentication.pending_deletion import delete_pending_deletion, get_pending_deletion
from server.src.store.cache.authentication.verify_otp import verify_otp
from server.src.store.sql.authentication.sessions.expire_all_sessions import expire_all_sessions
from server.src.store.sql.authentication.users.select_user_by_id import select_user_by_id
from server.src.store.sql.authentication.users.soft_delete_user import soft_delete_user

async def complete_deletion(pool: Pool, cache: Redis, lua_manager: LuaScriptManager, user_id: UUID, otp: str, country: str, device: str, publisher: RedisEventPublisher) -> None:
    pending = await get_pending_deletion(cache, str(user_id))
    if pending is None:
        raise PendingUserDeletionNotFoundError()

    if not await verify_otp(cache, pending.email_hash, otp):

        raise OtpVerificationError()

    async with pool.acquire() as conn:
        user = await select_user_by_id(conn, user_id)
        if user is None:
            raise UserNotFoundError()
        
        email = decrypt(user.email_encrypted)

        async with conn.transaction():
            await soft_delete_user(conn, user_id)
            await expire_all_sessions(conn, user_id)

    await expire_all_redis_sessions(cache, lua_manager, user_id)

    await publisher.publish(
        "session:invalidation",
        "EXPIRE_USER_SESSIONS_MEMORY",
        {"user_id": str(user_id)},
    )

    await delete_pending_deletion(cache, str(user_id))

    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = AccountDeletionSuccessTemplate(device=device, country=country, timestamp=timestamp)
    
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email,
        "subject": template.subject,
        "message": template.html
    })
