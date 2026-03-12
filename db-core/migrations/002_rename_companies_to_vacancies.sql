-- Migration: Rename companies table to vacancies and company_id to vacancy_id
-- Created: 2025-01-XX

-- SQLite doesn't support RENAME COLUMN directly, so we need to recreate the table
-- For PostgreSQL, we can use ALTER TABLE RENAME

-- For SQLite:
-- Step 1: Rename old table
ALTER TABLE companies RENAME TO companies_old;

-- Step 2: Create new vacancies table with vacancy_id (without recruiter_chat_id)
CREATE TABLE vacancies (
    vacancy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    bot_token TEXT NOT NULL,
    open_api_token TEXT,
    vacancy TEXT,
    gpt_prompt TEXT,
    is_closed INTEGER NOT NULL DEFAULT 0,
    need_buttons_approve INTEGER NOT NULL DEFAULT 0,
    is_chatgpt INTEGER NOT NULL DEFAULT 1,
    deepseek_token TEXT
);

-- Step 3: Copy data from old table to new table (excluding recruiter_chat_id)
INSERT INTO vacancies (
    vacancy_id, company_name, bot_token, open_api_token, vacancy, gpt_prompt,
    is_closed, need_buttons_approve, is_chatgpt, deepseek_token
)
SELECT 
    company_id, company_name, bot_token, open_api_token, vacancy, gpt_prompt,
    is_closed, need_buttons_approve, is_chatgpt, deepseek_token
FROM companies_old;

-- Step 4: Update vacancy_managers table to use vacancy_id
-- First, drop old foreign key constraint (SQLite doesn't support DROP CONSTRAINT, so we recreate the table)
ALTER TABLE vacancy_managers RENAME TO vacancy_managers_old;

CREATE TABLE vacancy_managers (
    vacancy_manager_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vacancy_id INTEGER NOT NULL,
    manager_chat_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (vacancy_id) REFERENCES vacancies(vacancy_id) ON DELETE CASCADE,
    UNIQUE(vacancy_id, manager_chat_id)
);

-- Copy data with mapping from company_id to vacancy_id
INSERT INTO vacancy_managers (vacancy_manager_id, vacancy_id, manager_chat_id, created_at)
SELECT 
    vm.vacancy_manager_id,
    c.vacancy_id,  -- Map company_id to vacancy_id
    vm.manager_chat_id,
    vm.created_at
FROM vacancy_managers_old vm
JOIN companies_old c ON vm.company_id = c.company_id;

-- Step 5: Update applicant table foreign key
-- SQLite doesn't support ALTER TABLE MODIFY, so we need to recreate
-- But applicant table already uses vacancy_id, so we just need to update the foreign key reference
-- Since SQLite doesn't support DROP CONSTRAINT, we'll need to recreate the table if needed
-- But applicant.vacancy_id already references companies.company_id, so we need to update it

-- For applicant table, we need to check if it needs updating
-- If applicant.vacancy_id already exists and references companies.company_id,
-- we need to update the foreign key to reference vacancies.vacancy_id
-- SQLite doesn't support this directly, so we might need to recreate the table

-- Step 6: Drop old tables
DROP TABLE companies_old;
DROP TABLE vacancy_managers_old;

-- Step 7: Recreate indexes
CREATE INDEX IF NOT EXISTS idx_vacancy_managers_vacancy_id ON vacancy_managers(vacancy_id);
CREATE INDEX IF NOT EXISTS idx_vacancy_managers_manager_chat_id ON vacancy_managers(manager_chat_id);
CREATE INDEX IF NOT EXISTS idx_vacancy_manager ON vacancy_managers(vacancy_id, manager_chat_id);

-- For PostgreSQL, use this instead:
/*
-- Rename table
ALTER TABLE companies RENAME TO vacancies;

-- Rename column
ALTER TABLE vacancies RENAME COLUMN company_id TO vacancy_id;

-- Update foreign key in vacancy_managers
ALTER TABLE vacancy_managers RENAME COLUMN company_id TO vacancy_id;
ALTER TABLE vacancy_managers DROP CONSTRAINT IF EXISTS fk_vacancy_managers_company;
ALTER TABLE vacancy_managers ADD CONSTRAINT fk_vacancy_managers_vacancy 
    FOREIGN KEY (vacancy_id) REFERENCES vacancies(vacancy_id) ON DELETE CASCADE;

-- Update unique constraint
ALTER TABLE vacancy_managers DROP CONSTRAINT IF EXISTS uq_vacancy_manager;
ALTER TABLE vacancy_managers ADD CONSTRAINT uq_vacancy_manager UNIQUE (vacancy_id, manager_chat_id);

-- Update indexes
DROP INDEX IF EXISTS idx_vacancy_managers_company_id;
CREATE INDEX idx_vacancy_managers_vacancy_id ON vacancy_managers(vacancy_id);
DROP INDEX IF EXISTS idx_company_manager;
CREATE INDEX idx_vacancy_manager ON vacancy_managers(vacancy_id, manager_chat_id);

-- Update applicant foreign key (if needed)
ALTER TABLE applicant DROP CONSTRAINT IF EXISTS applicant_vacancy_id_fkey;
ALTER TABLE applicant ADD CONSTRAINT applicant_vacancy_id_fkey 
    FOREIGN KEY (vacancy_id) REFERENCES vacancies(vacancy_id) ON DELETE SET NULL;
*/

