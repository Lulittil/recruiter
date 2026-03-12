-- Migration: Add count_report_offers column to vacancies table
-- Created: 2025-01-XX

-- Add count_report_offers column to vacancies table
-- For PostgreSQL:
ALTER TABLE vacancies ADD COLUMN IF NOT EXISTS count_report_offers INTEGER NOT NULL DEFAULT 0;

-- Note: The column defaults to 0, so existing records will have 0
-- which means no offer analysis available by default

