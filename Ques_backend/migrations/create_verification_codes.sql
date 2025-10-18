-- Create verification_codes table for SMS and email verification
-- This table stores verification codes for user registration and password reset

-- Drop table if it exists (for idempotency)
DROP TABLE IF EXISTS verification_codes CASCADE;

-- Create the verification_codes table
CREATE TABLE verification_codes (
    id SERIAL PRIMARY KEY,
    provider_type VARCHAR(50) NOT NULL,  -- 'PHONE', 'EMAIL', 'WECHAT', 'ALIPAY'
    provider_id VARCHAR(255) NOT NULL,   -- phone number or email address
    code VARCHAR(10) NOT NULL,           -- verification code
    purpose VARCHAR(50) NOT NULL,        -- 'REGISTRATION', 'PASSWORD_RESET', 'LOGIN', etc.
    expires_at TIMESTAMP NOT NULL,       -- when the code expires
    used_at TIMESTAMP,                   -- when the code was used (NULL if not used)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    attempts INTEGER NOT NULL DEFAULT 0  -- number of failed verification attempts
);

-- Create indexes for performance
CREATE INDEX idx_verification_codes_provider ON verification_codes(provider_type, provider_id);
CREATE INDEX idx_verification_codes_created_at ON verification_codes(created_at);
CREATE INDEX idx_verification_codes_expires_at ON verification_codes(expires_at);

-- Add comment
COMMENT ON TABLE verification_codes IS 'Stores verification codes for SMS and email verification';
