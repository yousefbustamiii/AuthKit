from uuid import UUID

from asyncpg import Connection

async def soft_delete_organization_member(conn: Connection, organization_id: UUID, user_id: UUID) -> None:
    query = """
    UPDATE organization_members
    SET is_deleted = TRUE
    WHERE organization_id = $1 AND user_id = $2 AND is_deleted = FALSE
    """
    await conn.execute(query, organization_id, user_id)
