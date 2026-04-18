from uuid import UUID

from asyncpg import Connection

async def update_organization(conn: Connection, organization_id: UUID, name: str) -> None:
    query = """
    UPDATE organizations
    SET name = $2
    WHERE organization_id = $1 AND is_deleted = FALSE
    """
    await conn.execute(query, organization_id, name)
