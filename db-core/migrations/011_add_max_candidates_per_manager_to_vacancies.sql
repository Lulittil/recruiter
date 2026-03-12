-- Migration: Add max_candidates_per_manager column to vacancies table
-- Created: 2025-01-XX

-- Add max_candidates_per_manager column to vacancies table
-- For PostgreSQL:
ALTER TABLE vacancies ADD COLUMN IF NOT EXISTS max_candidates_per_manager INTEGER;

-- Note: The column is nullable, so existing records will have NULL values
-- If NULL, there is no limit on the number of candidates per manager

