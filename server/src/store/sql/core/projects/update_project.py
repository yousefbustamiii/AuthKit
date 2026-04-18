from uuid import UUID

from asyncpg import Connection

async def update_project(conn: Connection, project_id: UUID, name: str) -> None:
    query = """
    UPDATE projects
    SET name = $2
    WHERE project_id = $1 AND is_deleted = FALSE
    """
    await conn.execute(query, project_id, name)
