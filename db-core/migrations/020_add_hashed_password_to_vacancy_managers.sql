-- Migration: Add hashed_password column to vacancy_managers table
-- Created: 2025-12-09

-- Add hashed_password column to vacancy_managers table
ALTER TABLE vacancy_managers 
ADD COLUMN IF NOT EXISTS hashed_password TEXT;

-- Add comment
COMMENT ON COLUMN vacancy_managers.hashed_password IS 'Хэшированный пароль менеджера (bcrypt) для входа в менеджерскую панель';

