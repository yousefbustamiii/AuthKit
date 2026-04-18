CREATE TABLE projects (
    project_id UUID PRIMARY KEY,

    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    name TEXT NOT NULL,

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    created_by_user_id UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Speeds up listing active projects per org and supports efficient ON DELETE CASCADE from organizations.
CREATE INDEX idx_projects_org_active ON projects (organization_id) WHERE is_deleted = FALSE;
