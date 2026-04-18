from uuid import UUID

from asyncpg import Connection

async def soft_delete_invitation(conn: Connection, invitation_id: UUID) -> bool:
    query = """
    UPDATE invitations
    SET is_deleted = TRUE
    WHERE invitation_id = $1 AND is_deleted = FALSE
    """
    status = await conn.execute(query, invitation_id)
    return int(status.split()[-1]) > 0
