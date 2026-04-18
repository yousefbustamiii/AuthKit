from dataclasses import dataclass
from uuid import UUID

from asyncpg import Connection

@dataclass
class CustomerByOrg:
    customer_id: UUID
    stripe_customer_id: str

async def select_customer_by_org(
    conn: Connection,
    organization_id: UUID,
) -> CustomerByOrg | None:
    query = """
    SELECT customer_id, stripe_customer_id
    FROM customers
    WHERE organization_id = $1
    LIMIT 1
    """

    row = await conn.fetchrow(query, organization_id)

    if row is None:
        return None

    return CustomerByOrg(
        customer_id=row["customer_id"],
        stripe_customer_id=row["stripe_customer_id"],
    )
