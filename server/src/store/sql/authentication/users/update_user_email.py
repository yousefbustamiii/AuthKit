from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.encryption.aes_encrypt import encrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

async def update_user_email(conn: Connection, user_id: UUID, email: str) -> None:
    email_hash = hash_blake2s(email)
    email_encrypted = encrypt(email)
    
    query = """
    UPDATE users
    SET email_hash = $2, email_encrypted = $3, updated_at = NOW()
    WHERE user_id = $1
    """
    
    await conn.execute(
        query,
        user_id,
        email_hash,
        email_encrypted
    )
