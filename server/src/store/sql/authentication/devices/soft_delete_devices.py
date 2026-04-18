from uuid import UUID

from asyncpg import Connection

async def soft_delete_devices(
    conn: Connection,
    user_id: UUID,
    device_ids: list[UUID],
) -> int:

    query = """
    WITH deleted_devices AS (
        UPDATE trusted_devices
        SET is_deleted = TRUE
        WHERE device_id = ANY($2::uuid[])
          AND user_id = $1
          AND is_deleted = FALSE
        RETURNING device_id
    ),
    expired_sessions AS (
        UPDATE sessions
        SET expires_at = NOW()
        WHERE device_id IN (SELECT device_id FROM deleted_devices)
          AND expires_at > NOW()
    )
    SELECT COUNT(*) FROM deleted_devices
    """

    count = await conn.fetchval(query, user_id, device_ids)
    return count or 0
