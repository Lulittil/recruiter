-- Добавление поля owner_id в таблицу admins
ALTER TABLE admins 
ADD COLUMN IF NOT EXISTS owner_id BIGINT UNIQUE;

-- Создание индекса для быстрого поиска по owner_id
CREATE INDEX IF NOT EXISTS idx_admins_owner_id ON admins(owner_id);

-- Комментарий к полю
COMMENT ON COLUMN admins.owner_id IS 'Telegram ID владельца (связь с вакансиями через owner_id)';

