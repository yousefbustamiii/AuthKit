from dataclasses import dataclass
from uuid import UUID, uuid7

from asyncpg import Connection

@dataclass
class InsertedNewApiKey:
    key_id: UUID
    old_key_hash: str

async def insert_new_api_key(
    conn: Connection,
    old_key_id: UUID,
    project_id: UUID,
    key_hash: str,
    key_encrypted: str,
    created_by_user_id: UUID,
) -> InsertedNewApiKey | None:
    new_key_id = uuid7()

    query = """
    WITH old_key AS (
        UPDATE api_keys
        SET is_deleted = TRUE
        WHERE key_id = $1
          AND is_deleted = FALSE
          AND project_id = $2
        RETURNING project_id, name, key_hash AS old_key_hash
    ),
    new_key AS (
        INSERT INTO api_keys (key_id, project_id, name, key_hash, key_encrypted, created_by_user_id, rotated_at)
        SELECT $3, project_id, name, $4, $5, $6, NOW()
        FROM old_key
        RETURNING key_id
    )
    SELECT new_key.key_id, old_key.old_key_hash
    FROM new_key, old_key
    """

    row = await conn.fetchrow(query, old_key_id, project_id, new_key_id, key_hash, key_encrypted, created_by_user_id)

    if row is None:
        return None

    return InsertedNewApiKey(key_id=row["key_id"], old_key_hash=row["old_key_hash"])
