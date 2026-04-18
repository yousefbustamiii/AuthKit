from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

@dataclass
class ProjectApiKeyRecord:
    key_id: UUID
    name: str
    created_by_user_id: UUID
    created_at: datetime
    rotated_at: datetime | None
    last_used_at: datetime | None
    
async def get_project_api_keys(conn: Connection, organization_id: UUID, project_id: UUID) -> list[ProjectApiKeyRecord]:
    query = """
    SELECT ak.key_id, ak.name, ak.created_by_user_id, ak.created_at, ak.rotated_at, ak.last_used_at
    FROM api_keys ak
    JOIN projects p ON p.project_id = ak.project_id
    WHERE ak.project_id = $1
      AND p.organization_id = $2
      AND ak.is_deleted = FALSE
      AND p.is_deleted = FALSE
    ORDER BY ak.created_at DESC
    """

    rows = await conn.fetch(query, project_id, organization_id)

    return [
        ProjectApiKeyRecord(
            key_id=row["key_id"],
            name=row["name"],
            created_by_user_id=row["created_by_user_id"],
            created_at=row["created_at"],
            rotated_at=row["rotated_at"],
            last_used_at=row["last_used_at"],
        )
        for row in rows
    ]
