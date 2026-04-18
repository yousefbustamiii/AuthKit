from dataclasses import dataclass
from uuid import UUID

from asyncpg import Connection

@dataclass
class CustomerByStripeId:
    customer_id: UUID
    organization_id: UUID

async def select_customer_by_stripe_id(
    conn: Connection,
    stripe_customer_id: str,
) -> CustomerByStripeId | None:
    query = """
    SELECT customer_id, organization_id
    FROM customers
    WHERE stripe_customer_id = $1
    """

    row = await conn.fetchrow(query, stripe_customer_id)

    if row is None:
        return None

    return CustomerByStripeId(
        customer_id=row["customer_id"],
        organization_id=row["organization_id"],
    )
