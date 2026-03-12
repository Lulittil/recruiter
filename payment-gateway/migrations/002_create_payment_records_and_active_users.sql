-- Миграция для создания таблиц payment_records и active_users

-- Таблица для хранения полных данных об оплате (соблюдение законодательства РФ)
CREATE TABLE IF NOT EXISTS payment_records (
    record_id SERIAL PRIMARY KEY,
    payment_id INTEGER UNIQUE NOT NULL,
    
    -- Данные о плательщике
    payer_type VARCHAR(20) NOT NULL,  -- 'individual' или 'legal_entity'
    telegram_user_id BIGINT NOT NULL,
    telegram_username VARCHAR(255),
    telegram_full_name VARCHAR(255),
    
    -- Для юридических лиц
    company_name VARCHAR(500),
    company_inn VARCHAR(12),
    company_kpp VARCHAR(9),
    company_ogrn VARCHAR(15),
    company_opf VARCHAR(100),
    company_address TEXT,
    company_email VARCHAR(255),
    
    -- Для физических лиц
    individual_full_name VARCHAR(255),
    individual_inn VARCHAR(12),
    
    -- Данные о платеже
    amount NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'RUB',
    vat_amount NUMERIC(10, 2),
    vat_rate NUMERIC(5, 2),
    tax_amount NUMERIC(10, 2),
    tax_rate INTEGER,
    
    -- Данные о тарифе
    tariff_id VARCHAR(50),
    tariff_name VARCHAR(255),
    
    -- Данные о провайдере платежа
    payment_provider VARCHAR(50),
    provider_payment_id VARCHAR(255),
    provider_transaction_id VARCHAR(255),
    
    -- Номера документов
    receipt_number VARCHAR(100),
    invoice_number VARCHAR(100),
    act_number VARCHAR(100),
    
    -- Статус и даты
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Дополнительные данные
    fiscal_data JSONB,
    payment_details JSONB,
    
    CONSTRAINT fk_payment_records_payment FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_payment_records_payment_id ON payment_records(payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_records_telegram_user_id ON payment_records(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_payment_records_company_inn ON payment_records(company_inn);
CREATE INDEX IF NOT EXISTS idx_payment_records_tariff_id ON payment_records(tariff_id);
CREATE INDEX IF NOT EXISTS idx_payment_records_payment_status ON payment_records(payment_status);
CREATE INDEX IF NOT EXISTS idx_payment_records_payment_date ON payment_records(payment_date);

-- Таблица для хранения данных о действующих пользователях
CREATE TABLE IF NOT EXISTS active_users (
    user_id SERIAL PRIMARY KEY,
    telegram_user_id BIGINT UNIQUE NOT NULL,
    telegram_username VARCHAR(255),
    telegram_full_name VARCHAR(255),
    telegram_link VARCHAR(500),
    
    -- Тип пользователя
    user_type VARCHAR(20) NOT NULL,  -- 'individual' или 'legal_entity'
    
    -- Для юридических лиц
    company_name VARCHAR(500),
    company_inn VARCHAR(12),
    company_kpp VARCHAR(9),
    company_ogrn VARCHAR(15),
    company_opf VARCHAR(100),
    company_address TEXT,
    company_email VARCHAR(255),
    
    -- Для физических лиц
    individual_full_name VARCHAR(255),
    individual_inn VARCHAR(12),
    
    -- Данные о тарифе
    current_tariff_id VARCHAR(50),
    current_tariff_name VARCHAR(255),
    tariff_purchased_at TIMESTAMP,
    tariff_expires_at TIMESTAMP,
    
    -- Лимиты тарифа
    tariff_vacancies_count INTEGER,
    tariff_offer_analyses_count INTEGER,
    
    -- Использованные лимиты
    used_vacancies_count INTEGER DEFAULT 0,
    used_offer_analyses_count INTEGER DEFAULT 0,
    
    -- Статус
    is_active BOOLEAN DEFAULT TRUE,
    access_granted_at TIMESTAMP,
    last_payment_date TIMESTAMP,
    
    -- Метаданные
    user_metadata JSONB,
    
    -- Даты
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_active_users_telegram_user_id ON active_users(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_active_users_company_inn ON active_users(company_inn);
CREATE INDEX IF NOT EXISTS idx_active_users_current_tariff_id ON active_users(current_tariff_id);
CREATE INDEX IF NOT EXISTS idx_active_users_is_active ON active_users(is_active);

