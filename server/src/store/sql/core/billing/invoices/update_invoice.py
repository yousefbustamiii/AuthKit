from asyncpg import Connection

async def update_invoice(
    conn: Connection,
    stripe_invoice_id: str,
    status: str,
    hosted_invoice_url: str | None = None,
) -> None:
    query = """
    UPDATE invoices
    SET status             = $2,
        hosted_invoice_url = COALESCE($3, hosted_invoice_url),
        updated_at         = NOW()
    WHERE stripe_invoice_id = $1
      AND is_deleted = FALSE
    """

    await conn.execute(query, stripe_invoice_id, status, hosted_invoice_url)
