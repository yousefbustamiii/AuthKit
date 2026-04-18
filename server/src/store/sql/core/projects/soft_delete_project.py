from uuid import UUID

from asyncpg import Connection

async def soft_delete_project(conn: Connection, project_id: UUID) -> None:
    query = """
    UPDATE projects
    SET is_deleted = TRUE
    WHERE project_id = $1 AND is_deleted = FALSE
    """
    await conn.execute(query, project_id)
