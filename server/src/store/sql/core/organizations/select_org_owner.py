from dataclasses import dataclass

from asyncpg import Connection

@dataclass
class OrgOwner:
    org_name: str
    email_encrypted: str

async def select_org_owner(
    conn: Connection,
    organization_id,
) -> OrgOwner | None:
    query = """
    SELECT o.name AS org_name, u.email_encrypted
    FROM organizations o
    JOIN users u ON u.user_id = o.owner_user_id
    WHERE o.organization_id = $1
      AND o.is_deleted = FALSE
    """

    row = await conn.fetchrow(query, organization_id)

    if row is None:
        return None

    return OrgOwner(
        org_name=row["org_name"],
        email_encrypted=row["email_encrypted"],
    )
