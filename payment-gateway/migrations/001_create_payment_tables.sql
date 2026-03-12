-- Миграция для создания таблиц Payment Gateway Service

-- Таблица платежей
CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    vacancy_id INTEGER,
    payment_type VARCHAR(20) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'RUB',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    provider VARCHAR(50),
    provider_payment_id VARCHAR(255),
    receipt_id INTEGER,
    invoice_id INTEGER,
    act_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_provider_payment_id ON payments(provider_payment_id);

-- Таблица чеков самозанятого
CREATE TABLE IF NOT EXISTS self_employed_receipts (
    receipt_id SERIAL PRIMARY KEY,
    payment_id INTEGER UNIQUE NOT NULL,
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    client_inn VARCHAR(12),
    client_type VARCHAR(20) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    tax_amount NUMERIC(10, 2) NOT NULL,
    tax_rate INTEGER NOT NULL,
    receipt_url VARCHAR(500),
    qr_code_url VARCHAR(500),
    fiscal_data JSONB,
    sent_to_client BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'created'
);

CREATE INDEX IF NOT EXISTS idx_receipts_payment_id ON self_employed_receipts(payment_id);
CREATE INDEX IF NOT EXISTS idx_receipts_receipt_number ON self_employed_receipts(receipt_number);

-- Внешние ключи
ALTER TABLE self_employed_receipts 
ADD CONSTRAINT fk_receipts_payment 
FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE CASCADE;

ALTER TABLE payments 
ADD CONSTRAINT fk_payments_receipt 
FOREIGN KEY (receipt_id) REFERENCES self_employed_receipts(receipt_id) ON DELETE SET NULL;

-- Таблица счетов (опционально)
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id SERIAL PRIMARY KEY,
    payment_id INTEGER,
    receipt_id INTEGER,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    inn VARCHAR(12),
    kpp VARCHAR(9),
    legal_address TEXT,
    amount NUMERIC(10, 2) NOT NULL,
    pdf_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'draft'
);

CREATE INDEX IF NOT EXISTS idx_invoices_payment_id ON invoices(payment_id);
CREATE INDEX IF NOT EXISTS idx_invoices_receipt_id ON invoices(receipt_id);

ALTER TABLE invoices 
ADD CONSTRAINT fk_invoices_payment 
FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE SET NULL;

ALTER TABLE invoices 
ADD CONSTRAINT fk_invoices_receipt 
FOREIGN KEY (receipt_id) REFERENCES self_employed_receipts(receipt_id) ON DELETE SET NULL;

ALTER TABLE payments 
ADD CONSTRAINT fk_payments_invoice 
FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE SET NULL;

-- Таблица актов (опционально)
CREATE TABLE IF NOT EXISTS acts (
    act_id SERIAL PRIMARY KEY,
    payment_id INTEGER,
    receipt_id INTEGER,
    act_number VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    inn VARCHAR(12),
    kpp VARCHAR(9),
    amount NUMERIC(10, 2) NOT NULL,
    pdf_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'draft'
);

CREATE INDEX IF NOT EXISTS idx_acts_payment_id ON acts(payment_id);
CREATE INDEX IF NOT EXISTS idx_acts_receipt_id ON acts(receipt_id);

ALTER TABLE acts 
ADD CONSTRAINT fk_acts_payment 
FOREIGN KEY (payment_id) REFERENCES payments(payment_id) ON DELETE SET NULL;

ALTER TABLE acts 
ADD CONSTRAINT fk_acts_receipt 
FOREIGN KEY (receipt_id) REFERENCES self_employed_receipts(receipt_id) ON DELETE SET NULL;

ALTER TABLE payments 
ADD CONSTRAINT fk_payments_act 
FOREIGN KEY (act_id) REFERENCES acts(act_id) ON DELETE SET NULL;

-- Таблица отслеживания дохода
CREATE TABLE IF NOT EXISTS income_tracking (
    tracking_id SERIAL PRIMARY KEY,
    year INTEGER UNIQUE NOT NULL,
    total_income NUMERIC(12, 2) DEFAULT 0,
    income_from_individuals NUMERIC(12, 2) DEFAULT 0,
    income_from_legal_entities NUMERIC(12, 2) DEFAULT 0,
    tax_paid NUMERIC(12, 2) DEFAULT 0,
    limit_exceeded BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_income_tracking_year ON income_tracking(year);

