from dataclasses import dataclass
from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.crypto.encryption.aes_encrypt import encrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.crypto.secrets.generate_project_api_key import generate_project_api_key
from server.src.app.errors.domains.core_errors import ApiKeyNotFoundError, InvalidRotateConfirmationError, OrgAccessDeniedError
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.logic.workers.api_key_cache_invalidation_listener import API_KEY_INVALIDATION_CHANNEL, INVALIDATE_API_KEY_CACHE
from server.src.store.sql.core.api_keys.insert_new_api_key import insert_new_api_key
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

@dataclass
class RotatedApiKey:
    key_id: UUID
    raw_key: str

async def rotate_project_api_key(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
    project_id: UUID,
    key_id: UUID,
    confirmation: str,
) -> RotatedApiKey:
    if confirmation.lower() != "rotate":
        raise InvalidRotateConfirmationError()

    role_result = await resolve_user_role_in_org(
        pool=pool,
        organization_id=organization_id,
        user_id=user_id,
        org_role_cache=org_role_cache,
    )

    if role_result.role is None:
        raise OrgAccessDeniedError()

    if role_result.role not in ("owner", "admin"):
        raise OrgAccessDeniedError()

    raw_key = generate_project_api_key()
    key_hash = hash_blake2s(raw_key)
    key_encrypted = encrypt(raw_key)

    async with pool.acquire() as conn:
        new_key = await insert_new_api_key(
            conn,
            old_key_id=key_id,
            project_id=project_id,
            key_hash=key_hash,
            key_encrypted=key_encrypted,
            created_by_user_id=user_id,
        )

        if new_key is None:
            raise ApiKeyNotFoundError()

    await RedisEventPublisher(cache).publish(
        API_KEY_INVALIDATION_CHANNEL,
        INVALIDATE_API_KEY_CACHE,
        {"key_hash": new_key.old_key_hash},
    )

    return RotatedApiKey(
        key_id=new_key.key_id,
        raw_key=raw_key,
    )
