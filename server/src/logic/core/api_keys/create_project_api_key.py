from dataclasses import dataclass
from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.crypto.encryption.aes_encrypt import encrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.crypto.secrets.generate_project_api_key import generate_project_api_key
from server.src.app.errors.domains.core_errors import InvalidApiKeyNameError, OrgAccessDeniedError
from server.src.app.validation.core.validate_core_names import validate_api_key_name
from server.src.store.sql.core.api_keys.insert_api_key import insert_api_key
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

@dataclass
class CreatedApiKey:
    key_id: UUID
    raw_key: str

async def create_project_api_key(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
    project_id: UUID,
    name: str,
) -> CreatedApiKey:
    ok, result = validate_api_key_name(name)
    if not ok:
        raise InvalidApiKeyNameError(result)

    validated_name = result

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
        api_key = await insert_api_key(
            conn,
            project_id=project_id,
            name=validated_name,
            key_hash=key_hash,
            key_encrypted=key_encrypted,
            created_by_user_id=user_id,
        )

    return CreatedApiKey(
        key_id=api_key.key_id,
        raw_key=raw_key,
    )
