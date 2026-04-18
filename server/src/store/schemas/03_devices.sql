CREATE TABLE trusted_devices (
    device_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id),
    device_token_hash TEXT NOT NULL,
    device_name TEXT, -- e.g. "Chrome on MacOS" -- NOTE: This is the user agent
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ, -- When the trust expires (e.g., 1 year)
    
    -- Status
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- PERFORMANCE INDEX:
-- Speeds up the login check: "Find this token for this user"
CREATE INDEX idx_trusted_devices_user_token 
ON trusted_devices (user_id, device_token_hash);

-- PERFORMANCE INDEX:
-- Speeds up the "Manage Devices" page: "Show me all active devices for this user"
CREATE INDEX idx_trusted_devices_user_active 
ON trusted_devices (user_id) 
WHERE is_deleted = FALSE;