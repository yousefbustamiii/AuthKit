CREATE TABLE invoices (
    invoice_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    stripe_invoice_id TEXT NOT NULL UNIQUE,
    stripe_subscription_id TEXT,

    amount INTEGER NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'open', 'paid', 'uncollectible', 'void')),

    hosted_invoice_url TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- stripe_invoice_id is already covered by its UNIQUE constraint above.
-- status is low-cardinality (5 values) — Postgres seq scans at this selectivity; not indexed.
CREATE INDEX idx_invoices_stripe_sub_id ON invoices (stripe_subscription_id);
CREATE INDEX idx_invoices_org_id ON invoices (organization_id);