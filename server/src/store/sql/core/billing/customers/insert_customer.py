from dataclasses import dataclass
from uuid import UUID, uuid7

from asyncpg import Connection

@dataclass
class InsertedCustomer:
    customer_id: UUID
    stripe_customer_id: str

async def insert_customer(
    conn: Connection,
    user_id: UUID,
    organization_id: UUID,
    stripe_customer_id: str,
) -> InsertedCustomer:
    customer_id = uuid7()

    query = """
    WITH ins AS (
        INSERT INTO customers (customer_id, user_id, organization_id, stripe_customer_id)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (organization_id) DO NOTHING
        RETURNING customer_id, stripe_customer_id
    )
    SELECT customer_id, stripe_customer_id FROM ins
    UNION ALL
    SELECT customer_id, stripe_customer_id FROM customers WHERE organization_id = $3
    LIMIT 1
    """

    row = await conn.fetchrow(query, customer_id, user_id, organization_id, stripe_customer_id)

    return InsertedCustomer(
        customer_id=row["customer_id"],
        stripe_customer_id=row["stripe_customer_id"],
    )

