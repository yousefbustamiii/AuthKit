from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

@dataclass
class SubscriptionByStripeId:
    subscription_id: UUID
    organization_id: UUID
    plan: str
    status: str
    current_period_end: datetime
    cancel_at_period_end: bool


async def select_subscription_by_stripe_id(
    conn: Connection,
    stripe_subscription_id: str,
) -> SubscriptionByStripeId | None:
    query = """
    SELECT subscription_id, organization_id, plan, status,
           current_period_end, cancel_at_period_end
    FROM subscriptions
    WHERE stripe_subscription_id = $1
      AND is_deleted = FALSE
    """

    row = await conn.fetchrow(query, stripe_subscription_id)

    if row is None:
        return None

    return SubscriptionByStripeId(
        subscription_id=row["subscription_id"],
        organization_id=row["organization_id"],
        plan=row["plan"],
        status=row["status"],
        current_period_end=row["current_period_end"],
        cancel_at_period_end=row["cancel_at_period_end"],
    )
