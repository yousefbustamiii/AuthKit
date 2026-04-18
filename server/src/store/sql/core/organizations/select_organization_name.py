from uuid import UUID

from asyncpg import Connection

async def select_organization_name(conn: Connection, organization_id: UUID) -> str | None:
    query = """
    SELECT name
    FROM organizations
    WHERE organization_id = $1 AND is_deleted = FALSE
    """
    row = await conn.fetchrow(query, organization_id)
    if row is None:
        return None
    return row["name"]
