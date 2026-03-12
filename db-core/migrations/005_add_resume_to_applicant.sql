-- Migration: Add resume column to applicant table
-- Created: 2025-01-XX

-- Add resume column to applicant table
-- For PostgreSQL:
ALTER TABLE applicant ADD COLUMN IF NOT EXISTS resume TEXT;

-- Note: The column is nullable, so existing records will have NULL values
-- which is correct - only applicants who have sent their resume will have this field populated

