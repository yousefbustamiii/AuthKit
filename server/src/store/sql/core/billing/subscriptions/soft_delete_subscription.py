from asyncpg import Connection

async def soft_delete_subscription(
    conn: Connection,
    stripe_subscription_id: str,
) -> None:
    query = """
    UPDATE subscriptions
    SET is_deleted = TRUE,
        status     = 'canceled',
        updated_at = NOW()
    WHERE stripe_subscription_id = $1
      AND is_deleted = FALSE
    """

    await conn.execute(query, stripe_subscription_id)
