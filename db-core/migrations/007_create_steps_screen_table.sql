-- Migration: Create steps_screen table for interview steps
-- Created: 2025-01-XX

-- Create steps_screen table
-- For PostgreSQL:
CREATE TABLE IF NOT EXISTS steps_screen (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- Insert initial steps
INSERT INTO steps_screen (id, name) VALUES
    (0, 'получено согласие'),
    (1, 'получен отчет после скрининга'),
    (2, 'приглашен на второй этап'),
    (3, 'отказ после первого этапа'),
    (4, 'прошел второй этап'),
    (5, 'отказ после второго этапа')
ON CONFLICT (id) DO NOTHING;

-- Note: Using ON CONFLICT to prevent errors if migration is run multiple times

