from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import DeletionTemplate
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.crypto.secrets.generate_otp import generate_otp
from server.src.app.errors.domains.authentication_errors import UserNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.store.cache.authentication.pending_deletion import store_pending_deletion
from server.src.store.cache.authentication.store_otp import store_otp
from server.src.store.sql.authentication.users.select_user_by_id import select_user_by_id

@dataclass
class InitiateDeletionResult:
    user_id: str

async def initiate_deletion(pool: Pool, cache: Redis, lua_manager: LuaScriptManager, user_id: UUID, country: str, device: str) -> InitiateDeletionResult:
    async with pool.acquire() as conn:
        user = await select_user_by_id(conn, user_id)

    if user is None:
        raise UserNotFoundError()

    email = decrypt(user.email_encrypted)
    email_hash = hash_blake2s(email)
    otp = generate_otp()

    await store_pending_deletion(cache, lua_manager, str(user_id), email_hash)
    await store_otp(cache, email_hash, otp)
    
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = DeletionTemplate(otp=otp, device=device, country=country, timestamp=timestamp)
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email, 
        "subject": template.subject, 
        "message": template.html
    })

    return InitiateDeletionResult(user_id=str(user_id))
