-- Создание таблицы админов для admin-panel
CREATE TABLE IF NOT EXISTS admins (
    admin_id VARCHAR(64) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_admins_username ON admins(username);
CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);
CREATE INDEX IF NOT EXISTS idx_admins_is_active ON admins(is_active);

-- Комментарии к таблице
COMMENT ON TABLE admins IS 'Администраторы веб-админки';
COMMENT ON COLUMN admins.admin_id IS 'Уникальный идентификатор администратора';
COMMENT ON COLUMN admins.username IS 'Имя пользователя (уникальное)';
COMMENT ON COLUMN admins.email IS 'Email адрес (уникальный)';
COMMENT ON COLUMN admins.hashed_password IS 'Хэшированный пароль (bcrypt)';
COMMENT ON COLUMN admins.is_active IS 'Активен ли аккаунт';

