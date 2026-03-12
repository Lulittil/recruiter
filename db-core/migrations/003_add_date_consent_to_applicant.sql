-- Migration: Add date_consent column to applicant table
-- Created: 2025-01-XX

-- Add date_consent column to applicant table
-- For SQLite:
-- ALTER TABLE applicant ADD COLUMN date_consent TIMESTAMP;

-- For PostgreSQL:
ALTER TABLE applicant ADD COLUMN IF NOT EXISTS date_consent TIMESTAMP WITH TIME ZONE;

-- Note: The column is nullable, so existing records will have NULL values
-- which is correct - only new consents will have this field populated

