from uuid import UUID

from asyncpg import Connection

async def soft_delete_api_key(conn: Connection, key_id: UUID, project_id: UUID) -> str | None:
    query = """
    UPDATE api_keys
    SET is_deleted = TRUE
    WHERE key_id = $1
      AND is_deleted = FALSE
      AND project_id = $2
    RETURNING key_hash
    """
    return await conn.fetchval(query, key_id, project_id)
