from asyncpg import Connection

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

async def expire_session(conn: Connection, session_token: str) -> None:
    session_token_hash = hash_blake2s(session_token)
    
    query = """
    UPDATE sessions
    SET expires_at = NOW()
    WHERE 
        session_token_hash = $1
        AND expires_at > NOW()
    """
    
    await conn.execute(query, session_token_hash)
