from uuid import UUID

from asyncpg import Connection

async def soft_delete_organization(conn: Connection, organization_id: UUID) -> None:
    query = """
    UPDATE organizations
    SET is_deleted = TRUE
    WHERE organization_id = $1 AND is_deleted = FALSE
    """
    await conn.execute(query, organization_id)
