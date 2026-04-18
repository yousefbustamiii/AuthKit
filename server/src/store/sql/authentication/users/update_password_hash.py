from uuid import UUID

from asyncpg import Connection

async def update_password_hash(conn: Connection, user_id: UUID, new_password_hash: str) -> None:
    query = """
    UPDATE users
    SET password_hash = $2, updated_at = NOW()
    WHERE user_id = $1 AND is_deleted = FALSE
    """
    await conn.execute(query, user_id, new_password_hash)
