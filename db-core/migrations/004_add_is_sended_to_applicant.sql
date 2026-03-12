-- Migration: Add is_sended column to applicant table
-- Created: 2025-01-XX

-- Add is_sended column to applicant table
-- For PostgreSQL:
ALTER TABLE applicant ADD COLUMN IF NOT EXISTS is_sended BOOLEAN NOT NULL DEFAULT false;

-- Note: The column defaults to false, so existing records will have false
-- which is correct - only reports that are sent will have this field set to true

