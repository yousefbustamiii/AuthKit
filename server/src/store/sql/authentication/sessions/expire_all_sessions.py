from uuid import UUID

from asyncpg import Connection

async def expire_all_sessions(conn: Connection, user_id: UUID) -> None:
    query = """
    UPDATE sessions
    SET expires_at = LEAST(expires_at, NOW())
    WHERE user_id = $1 AND expires_at > NOW()
    """
    
    await conn.execute(query, user_id)
