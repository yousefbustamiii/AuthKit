from dataclasses import dataclass
from uuid import UUID, uuid7

from asyncpg import Connection

@dataclass
class InsertedInvoice:
    invoice_id: UUID

async def insert_invoice(
    conn: Connection,
    customer_id: UUID,
    organization_id: UUID,
    stripe_invoice_id: str,
    amount: int,
    currency: str,
    status: str,
    hosted_invoice_url: str | None = None,
    stripe_subscription_id: str | None = None,
) -> InsertedInvoice:
    invoice_id = uuid7()

    query = """
    INSERT INTO invoices (
        invoice_id, customer_id, organization_id, stripe_invoice_id,
        amount, currency, status, hosted_invoice_url, stripe_subscription_id
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    ON CONFLICT (stripe_invoice_id) DO UPDATE
        SET status                = EXCLUDED.status,
            hosted_invoice_url    = COALESCE(EXCLUDED.hosted_invoice_url, invoices.hosted_invoice_url),
            stripe_subscription_id = COALESCE(EXCLUDED.stripe_subscription_id, invoices.stripe_subscription_id)
    RETURNING invoice_id
    """

    row = await conn.fetchrow(
        query,
        invoice_id,
        customer_id,
        organization_id,
        stripe_invoice_id,
        amount,
        currency,
        status,
        hosted_invoice_url,
        stripe_subscription_id,
    )

    return InsertedInvoice(invoice_id=row["invoice_id"])

