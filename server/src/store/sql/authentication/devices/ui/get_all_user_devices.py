from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

@dataclass
class UserDevice:
    device_id: UUID
    device_name: str | None
    created_at: datetime
    expires_at: datetime | None

async def get_all_user_devices(conn: Connection, user_id: UUID) -> list[UserDevice]:
    query = """
    SELECT 
        device_id, 
        device_name, 
        created_at, 
        expires_at
    FROM trusted_devices
    WHERE user_id = $1
      AND is_deleted = FALSE
      AND (expires_at IS NULL OR expires_at > NOW())
    ORDER BY created_at DESC
    LIMIT 11
    """
    
    rows = await conn.fetch(query, user_id)
    
    return [
        UserDevice(
            device_id=row["device_id"],
            device_name=row["device_name"],
            created_at=row["created_at"],
            expires_at=row["expires_at"]
        )
        for row in rows
    ]
