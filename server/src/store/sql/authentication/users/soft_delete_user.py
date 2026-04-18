from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.encryption.aes_decrypt import decrypt

async def soft_delete_user(conn: Connection, user_id: UUID) -> str | None:
    query = """
    UPDATE users
    SET is_deleted = TRUE, updated_at = NOW()
    WHERE user_id = $1 
      AND is_deleted = FALSE
    RETURNING email_encrypted
    """
    
    email_encrypted = await conn.fetchval(query, user_id)
    
    if email_encrypted:
        return decrypt(email_encrypted)
    
    return None
