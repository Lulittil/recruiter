-- Migration: Add distribution_strategy column to vacancies table
-- Created: 2025-01-XX

-- Add distribution_strategy column to vacancies table
-- For PostgreSQL:
ALTER TABLE vacancies ADD COLUMN IF NOT EXISTS distribution_strategy TEXT DEFAULT 'manual';

-- Note: Default value is 'manual' - all managers receive notifications (current behavior)
-- Possible values: 'round_robin', 'least_loaded', 'random', 'manual'

