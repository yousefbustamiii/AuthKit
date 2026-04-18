from dataclasses import dataclass
from uuid import UUID, uuid7

from asyncpg import Connection

@dataclass
class InsertedApiKey:
    key_id: UUID

async def insert_api_key(
    conn: Connection,
    project_id: UUID,
    name: str,
    key_hash: str,
    key_encrypted: str,
    created_by_user_id: UUID,
) -> InsertedApiKey:
    key_id = uuid7()

    query = """
    INSERT INTO api_keys (key_id, project_id, name, key_hash, key_encrypted, created_by_user_id)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING key_id
    """

    row = await conn.fetchrow(query, key_id, project_id, name, key_hash, key_encrypted, created_by_user_id)

    return InsertedApiKey(key_id=row["key_id"])
