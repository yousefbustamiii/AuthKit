from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

@dataclass
class SelectedDevice:
    device_id: UUID
    user_id: UUID
    device_name: str | None
    expires_at: datetime | None

async def select_device_by_token_hash(
    conn: Connection,
    user_id: UUID,
    device_token: str,
) -> SelectedDevice | None:
    device_token_hash = hash_blake2s(device_token)

    query = """
    SELECT device_id, user_id, device_name, expires_at
    FROM trusted_devices
    WHERE user_id = $1
      AND device_token_hash = $2
      AND is_deleted = FALSE
      AND (expires_at IS NULL OR expires_at > NOW())
    LIMIT 1
    """

    row = await conn.fetchrow(query, user_id, device_token_hash)
    if row is None:
        return None

    return SelectedDevice(
        device_id=row["device_id"],
        user_id=row["user_id"],
        device_name=row["device_name"],
        expires_at=row["expires_at"]
    )
