-- Add owner_id column to vacancies table
-- This column stores the Telegram chat_id of the user who owns/manages the vacancy through core-bot

ALTER TABLE vacancies
ADD COLUMN owner_id BIGINT;

-- Create index for faster lookups by owner_id
CREATE INDEX IF NOT EXISTS idx_vacancies_owner_id ON vacancies(owner_id);

-- Add comment to the column
COMMENT ON COLUMN vacancies.owner_id IS 'Telegram chat_id of the user who owns this vacancy (for core-bot access control)';

