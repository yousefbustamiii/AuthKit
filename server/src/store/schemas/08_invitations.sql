CREATE TABLE invitations (
    invitation_id UUID PRIMARY KEY,

    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    invited_by_user_id UUID NOT NULL REFERENCES users(user_id),

    email_hash TEXT NOT NULL,
    email_encrypted TEXT NOT NULL,
    invitation_token_hash TEXT NOT NULL,

    role TEXT NOT NULL CHECK (role IN ('admin', 'member')),

    expires_at TIMESTAMPTZ NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (invitation_token_hash)
);

CREATE UNIQUE INDEX one_active_invite_per_email_per_org
    ON invitations (organization_id, email_hash)
    WHERE is_deleted = FALSE;
