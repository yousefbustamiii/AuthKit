from asyncpg import Pool

from server.src.store.sql.core.billing.invoices.update_invoice import update_invoice

async def handle_invoice_status_updated(pool: Pool, data_obj: dict) -> None:
    stripe_invoice_id: str | None = data_obj.get("id")
    if not stripe_invoice_id:
        return

    status: str | None = data_obj.get("status")
    if not status:
        return

    hosted_invoice_url: str | None = data_obj.get("hosted_invoice_url")

    async with pool.acquire() as conn:
        await update_invoice(
            conn,
            stripe_invoice_id=stripe_invoice_id,
            status=status,
            hosted_invoice_url=hosted_invoice_url,
        )
