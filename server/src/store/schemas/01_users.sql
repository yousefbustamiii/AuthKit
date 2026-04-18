CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  email_encrypted TEXT NOT NULL,
  email_hash TEXT NOT NULL,
  password_hash TEXT,  -- NULL for OAuth-only users (provider != 'email')
  name TEXT,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

  -- Account Information
  account_status TEXT NOT NULL DEFAULT 'active',
  provider TEXT NOT NULL DEFAULT 'email', CHECK (provider IN ('email', 'google', 'github')),
  avatar_url TEXT,

  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Enforce: email users must always have a password hash
  CONSTRAINT chk_email_provider_password CHECK (
    provider != 'email' OR password_hash IS NOT NULL
  )
);

-- Unique index for active users email (Excludes normal deleted, Includes Banned)
CREATE UNIQUE INDEX idx_users_email_active_user 
ON users (email_hash) 
WHERE is_deleted = FALSE;
