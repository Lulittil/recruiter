-- Migration: Add email column to vacancy_managers table
-- Created: 2025-12-09

-- Add email column to vacancy_managers table
ALTER TABLE vacancy_managers 
ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Create index for email lookups
CREATE INDEX IF NOT EXISTS idx_vacancy_managers_email 
    ON vacancy_managers(email);

-- Add comment
COMMENT ON COLUMN vacancy_managers.email IS 'Email адрес менеджера для идентификации в видеоконференциях';

