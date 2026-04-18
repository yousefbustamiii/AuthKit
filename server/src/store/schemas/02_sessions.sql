CREATE TABLE sessions (
  session_id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(user_id),
  device_id UUID REFERENCES trusted_devices(device_id),
  session_token_hash TEXT UNIQUE NOT NULL,
  country TEXT NOT NULL,
  device TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);

-- Covers: all user_id-only filters (leading column) + the CTE ORDER BY created_at DESC OFFSET 4.
CREATE INDEX idx_sessions_user_created ON sessions (user_id, created_at DESC);