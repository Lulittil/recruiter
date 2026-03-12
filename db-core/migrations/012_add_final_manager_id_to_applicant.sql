-- Migration: Add final_manager_id column to applicant table
-- Created: 2025-01-XX

-- Add final_manager_id column to applicant table
-- For PostgreSQL:
ALTER TABLE applicant ADD COLUMN IF NOT EXISTS final_manager_id INTEGER;

-- Add foreign key constraint
ALTER TABLE applicant ADD CONSTRAINT IF NOT EXISTS fk_applicant_final_manager 
    FOREIGN KEY (final_manager_id) REFERENCES vacancy_managers(vacancy_manager_id) ON DELETE SET NULL;

-- Note: The column is nullable, so existing records will have NULL values
-- This field stores the manager who made the final decision (invited or rejected)

