from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection


@dataclass
class BillingCustomerRecord:
    customer_id: UUID
    stripe_customer_id: str


@dataclass
class BillingSubscriptionRecord:
    subscription_id: UUID
    stripe_subscription_id: str
    stripe_item_id: str
    plan: str
    status: str
    current_period_end: datetime
    cancel_at_period_end: bool
    trial_end: datetime | None


@dataclass
class BillingInvoiceRecord:
    invoice_id: UUID
    stripe_invoice_id: str
    stripe_subscription_id: str | None
    amount: int
    currency: str
    status: str
    hosted_invoice_url: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class OrganizationBillingRecord:
    customer: BillingCustomerRecord | None
    subscription: BillingSubscriptionRecord | None
    invoices: list[BillingInvoiceRecord]


async def get_organization_billing(conn: Connection, organization_id: UUID) -> OrganizationBillingRecord:
    customer_row = await conn.fetchrow(
        """
        SELECT customer_id, stripe_customer_id
        FROM customers
        WHERE organization_id = $1
        LIMIT 1
        """,
        organization_id,
    )

    subscription_row = await conn.fetchrow(
        """
        SELECT
            subscription_id, stripe_subscription_id, stripe_item_id, plan, status,
            current_period_end, cancel_at_period_end, trial_end
        FROM subscriptions
        WHERE organization_id = $1
          AND is_deleted = FALSE
        ORDER BY created_at DESC
        LIMIT 1
        """,
        organization_id,
    )

    invoice_rows = await conn.fetch(
        """
        SELECT
            invoice_id, stripe_invoice_id, stripe_subscription_id, amount, currency,
            status, hosted_invoice_url, created_at, updated_at
        FROM invoices
        WHERE organization_id = $1
          AND is_deleted = FALSE
        ORDER BY created_at DESC
        """,
        organization_id,
    )

    return OrganizationBillingRecord(
        customer=None
        if customer_row is None
        else BillingCustomerRecord(
            customer_id=customer_row["customer_id"],
            stripe_customer_id=customer_row["stripe_customer_id"],
        ),
        subscription=None
        if subscription_row is None
        else BillingSubscriptionRecord(
            subscription_id=subscription_row["subscription_id"],
            stripe_subscription_id=subscription_row["stripe_subscription_id"],
            stripe_item_id=subscription_row["stripe_item_id"],
            plan=subscription_row["plan"],
            status=subscription_row["status"],
            current_period_end=subscription_row["current_period_end"],
            cancel_at_period_end=subscription_row["cancel_at_period_end"],
            trial_end=subscription_row["trial_end"],
        ),
        invoices=[
            BillingInvoiceRecord(
                invoice_id=row["invoice_id"],
                stripe_invoice_id=row["stripe_invoice_id"],
                stripe_subscription_id=row["stripe_subscription_id"],
                amount=row["amount"],
                currency=row["currency"],
                status=row["status"],
                hosted_invoice_url=row["hosted_invoice_url"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in invoice_rows
        ],
    )
