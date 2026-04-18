from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid7

from asyncpg import Connection

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

@dataclass
class InsertedDevice:
    device_id: UUID
    expires_at: datetime

async def insert_device(
    conn: Connection,
    user_id: UUID,
    device_token: str,
    device_name: str,
) -> InsertedDevice:
    device_token_hash = hash_blake2s(device_token)
    device_id = uuid7()

    query = """
    WITH to_kill AS (
        SELECT device_id
        FROM trusted_devices
        WHERE user_id = $2
          AND is_deleted = FALSE
          AND expires_at > NOW()
        ORDER BY created_at DESC
        OFFSET 9
    ),
    killed AS (
        UPDATE trusted_devices
        SET is_deleted = TRUE, expires_at = NOW()
        WHERE device_id IN (SELECT device_id FROM to_kill)
    )
    INSERT INTO trusted_devices (device_id, user_id, device_token_hash, device_name, expires_at)
    VALUES ($1, $2, $3, $4, NOW() + INTERVAL '1 year')
    RETURNING device_id, expires_at
    """

    row = await conn.fetchrow(query, device_id, user_id, device_token_hash, device_name)

    return InsertedDevice(
        device_id=row["device_id"],
        expires_at=row["expires_at"]
    )
