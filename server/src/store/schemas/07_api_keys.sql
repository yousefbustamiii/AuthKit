CREATE TABLE api_keys (
    key_id UUID PRIMARY KEY,

    project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    key_encrypted TEXT NOT NULL,

    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    created_by_user_id UUID NOT NULL REFERENCES users(user_id),

    rotated_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Hot path: API key validation on every authenticated request.
CREATE INDEX idx_api_keys_key_hash_active ON api_keys (key_hash) WHERE is_deleted = FALSE;

-- Speeds up listing keys per project and supports efficient ON DELETE CASCADE from projects.
CREATE INDEX idx_api_keys_project_active ON api_keys (project_id) WHERE is_deleted = FALSE;
