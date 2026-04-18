CREATE TABLE subscriptions (
    subscription_id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    stripe_subscription_id TEXT NOT NULL UNIQUE,
    stripe_item_id TEXT NOT NULL,

    plan TEXT NOT NULL CHECK (plan IN ('plan_1', 'plan_2', 'plan_3', 'unknown')),
    status TEXT NOT NULL CHECK (status IN ('active', 'trialing', 'past_due', 'canceled', 'unpaid', 'incomplete', 'incomplete_expired', 'paused')),

    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
    trial_end TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- stripe_subscription_id is already covered by its UNIQUE constraint above.
-- status is low-cardinality (8 values) — Postgres seq scans at this selectivity; not indexed.
CREATE INDEX idx_subscriptions_org_id ON subscriptions (organization_id);
CREATE INDEX idx_subscriptions_customer_id ON subscriptions (customer_id);

-- Enforce at most one non-deleted, non-canceled subscription per organization.
-- Canceled rows are intentionally allowed to accumulate for billing history.
CREATE UNIQUE INDEX idx_subscriptions_unique_active_org
    ON subscriptions (organization_id)
    WHERE is_deleted = FALSE AND status != 'canceled';