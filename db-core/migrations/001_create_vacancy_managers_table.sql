-- Migration: Create vacancy_managers table for many-to-many relationship
-- between companies (vacancies) and managers
-- Created: 2025-01-XX

-- Create vacancy_managers table
CREATE TABLE IF NOT EXISTS vacancy_managers (
    vacancy_manager_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    manager_chat_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Foreign key constraint
    CONSTRAINT fk_vacancy_managers_company 
        FOREIGN KEY (company_id) 
        REFERENCES companies(company_id) 
        ON DELETE CASCADE,
    
    -- Unique constraint to prevent duplicate manager-vacancy pairs
    CONSTRAINT uq_vacancy_manager 
        UNIQUE (company_id, manager_chat_id)
);

-- Create indexes for optimization
CREATE INDEX IF NOT EXISTS idx_vacancy_managers_company_id 
    ON vacancy_managers(company_id);

CREATE INDEX IF NOT EXISTS idx_vacancy_managers_manager_chat_id 
    ON vacancy_managers(manager_chat_id);

-- Composite index for fast lookups by both fields
CREATE INDEX IF NOT EXISTS idx_company_manager 
    ON vacancy_managers(company_id, manager_chat_id);

-- Note: For PostgreSQL, use:
-- CREATE TABLE IF NOT EXISTS vacancy_managers (
--     vacancy_manager_id SERIAL PRIMARY KEY,
--     company_id INTEGER NOT NULL,
--     manager_chat_id BIGINT NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
--     
--     CONSTRAINT fk_vacancy_managers_company 
--         FOREIGN KEY (company_id) 
--         REFERENCES companies(company_id) 
--         ON DELETE CASCADE,
--     
--     CONSTRAINT uq_vacancy_manager 
--         UNIQUE (company_id, manager_chat_id)
-- );
-- 
-- CREATE INDEX IF NOT EXISTS idx_vacancy_managers_company_id 
--     ON vacancy_managers(company_id);
-- 
-- CREATE INDEX IF NOT EXISTS idx_vacancy_managers_manager_chat_id 
--     ON vacancy_managers(manager_chat_id);
-- 
-- CREATE INDEX IF NOT EXISTS idx_company_manager 
--     ON vacancy_managers(company_id, manager_chat_id);

