-- Migration: Add step_screen_id column to applicant table
-- Created: 2025-01-XX

-- Add step_screen_id column to applicant table
-- For PostgreSQL:
ALTER TABLE applicant ADD COLUMN IF NOT EXISTS step_screen_id INTEGER;

-- Add foreign key constraint
ALTER TABLE applicant ADD CONSTRAINT IF NOT EXISTS fk_applicant_step_screen 
    FOREIGN KEY (step_screen_id) REFERENCES steps_screen(id) ON DELETE SET NULL;

-- Note: The column is nullable, so existing records will have NULL values
-- which is correct - only applicants with assigned step will have this field populated

