from datetime import datetime

from asyncpg import Connection

async def update_subscription(
    conn: Connection,
    stripe_subscription_id: str,
    status: str,
    plan: str,
    current_period_end: datetime,
    cancel_at_period_end: bool,
    trial_end: datetime | None = None,
    stripe_item_id: str | None = None,
) -> None:
    query = """
    UPDATE subscriptions
    SET status               = $2,
        plan                 = $3,
        current_period_end   = $4,
        cancel_at_period_end = $5,
        trial_end            = $6,
        stripe_item_id       = COALESCE($7, stripe_item_id),
        updated_at           = NOW()
    WHERE stripe_subscription_id = $1
      AND is_deleted = FALSE
    """

    await conn.execute(
        query,
        stripe_subscription_id,
        status,
        plan,
        current_period_end,
        cancel_at_period_end,
        trial_end,
        stripe_item_id,
    )
