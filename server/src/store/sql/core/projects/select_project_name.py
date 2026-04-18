from uuid import UUID

from asyncpg import Connection

async def select_project_name(conn: Connection, project_id: UUID) -> str | None:
    query = """
    SELECT name
    FROM projects
    WHERE project_id = $1 AND is_deleted = FALSE
    """
    row = await conn.fetchrow(query, project_id)
    if row is None:
        return None
    return row["name"]
