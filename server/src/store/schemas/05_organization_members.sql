CREATE TABLE organization_members (
    organization_member_id UUID PRIMARY KEY,

    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id),

    role TEXT NOT NULL DEFAULT 'owner' CHECK (role IN ('owner','admin','member')),

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    invited_by_user_id UUID REFERENCES users(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
);

CREATE UNIQUE INDEX one_owner_per_org
    ON organization_members (organization_id)
    WHERE role = 'owner' AND is_deleted = FALSE;

-- Enforces one active membership per user per org (replaces the invalid inline UNIQUE expression).
-- Also the hot path index: every auth check hits (organization_id, user_id) WHERE is_deleted = FALSE.
CREATE UNIQUE INDEX idx_org_members_org_user_active
    ON organization_members (organization_id, user_id)
    WHERE is_deleted = FALSE;
