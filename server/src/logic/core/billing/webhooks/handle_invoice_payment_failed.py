from datetime import datetime, timezone

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import BillingPaymentFailedTemplate
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.events.event_emitter import event_emitter
from server.src.store.sql.core.billing.customers.select_customer_by_stripe_id import select_customer_by_stripe_id
from server.src.store.sql.core.billing.invoices.insert_invoice import insert_invoice
from server.src.store.sql.core.organizations.select_org_owner import select_org_owner

async def handle_invoice_payment_failed(pool: Pool, cache: Redis, data_obj: dict) -> None:
    stripe_customer_id: str | None = data_obj.get("customer")
    if not stripe_customer_id:
        return

    async with pool.acquire() as conn:
        customer = await select_customer_by_stripe_id(conn, stripe_customer_id)

        if customer is None:
            return  # Not from our system

        await insert_invoice(
            conn,
            customer_id=customer.customer_id,
            organization_id=customer.organization_id,
            stripe_invoice_id=data_obj["id"],
            amount=data_obj.get("amount_due", 0),
            currency=data_obj.get("currency", "usd"),
            status=data_obj.get("status", "open"),
            hosted_invoice_url=data_obj.get("hosted_invoice_url"),
            stripe_subscription_id=data_obj.get("subscription"),
        )
        owner = await select_org_owner(conn, customer.organization_id)

    if owner is None:
        return

    email = decrypt(owner.email_encrypted)
    amount_cents: int = data_obj.get("amount_due", 0)
    currency: str = data_obj.get("currency", "usd").upper()
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = BillingPaymentFailedTemplate(
        org_name=owner.org_name,
        amount=f"${amount_cents / 100:.2f}",
        currency=currency,
        invoice_url=data_obj.get("hosted_invoice_url") or "",
        timestamp=timestamp,
    )
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email,
        "subject": template.subject,
        "message": template.html,
    })
