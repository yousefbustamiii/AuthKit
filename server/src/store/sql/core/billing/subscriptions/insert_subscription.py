from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid7

from asyncpg import Connection

@dataclass
class InsertedSubscription:
    subscription_id: UUID


async def insert_subscription(
    conn: Connection,
    organization_id: UUID,
    customer_id: UUID,
    stripe_subscription_id: str,
    stripe_item_id: str,
    plan: str,
    status: str,
    current_period_end: datetime,
    cancel_at_period_end: bool = False,
    trial_end: datetime | None = None,
) -> InsertedSubscription:
    subscription_id = uuid7()

    query = """
    INSERT INTO subscriptions (
        subscription_id, organization_id, customer_id, stripe_subscription_id, stripe_item_id,
        plan, status, current_period_end, cancel_at_period_end, trial_end
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    ON CONFLICT (stripe_subscription_id) DO UPDATE
        SET plan               = EXCLUDED.plan,
            status             = EXCLUDED.status,
            current_period_end = EXCLUDED.current_period_end,
            cancel_at_period_end = EXCLUDED.cancel_at_period_end,
            trial_end          = COALESCE(EXCLUDED.trial_end, subscriptions.trial_end),
            updated_at         = NOW()
    RETURNING subscription_id
    """

    row = await conn.fetchrow(
        query,
        subscription_id,
        organization_id,
        customer_id,
        stripe_subscription_id,
        stripe_item_id,
        plan,
        status,
        current_period_end,
        cancel_at_period_end,
        trial_end,
    )

    return InsertedSubscription(subscription_id=row["subscription_id"])
