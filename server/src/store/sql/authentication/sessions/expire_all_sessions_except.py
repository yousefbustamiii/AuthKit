from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

async def expire_all_sessions_except(conn: Connection, user_id: UUID, session_token: str) -> None:
    
    session_token_hash = hash_blake2s(session_token)
    query = """
    UPDATE sessions
    SET expires_at = NOW()
    WHERE user_id = $1 AND session_token_hash != $2 AND expires_at > NOW()
    """
    
    await conn.execute(query, user_id, session_token_hash)
