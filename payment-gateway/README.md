# Payment Gateway Service

Сервис для обработки платежей от юридических лиц и генерации чеков самозанятого.

## Описание

Payment Gateway Service обрабатывает платежи от юридических лиц через платежные системы (Robokassa, ЮKassa) и автоматически генерирует чеки самозанятого через интеграцию с "Мой налог".

## Возможности

- ✅ Обработка платежей от юридических лиц
- ✅ Интеграция с Robokassa
- ✅ Генерация чеков самозанятого
- ✅ Автоматический учет дохода и налога
- ✅ Отслеживание лимита дохода (2.4 млн/год)
- ✅ Webhook'и от платежных систем

## Структура проекта

```
payment-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Конфигурация
│   ├── database.py          # Настройка БД
│   ├── models.py            # SQLAlchemy модели
│   ├── schemas.py           # Pydantic схемы
│   ├── payment_providers/   # Провайдеры платежей
│   │   ├── base.py
│   │   └── robokassa.py
│   ├── routers/            # API роутеры
│   │   ├── payments.py
│   │   └── webhooks.py
│   └── services/           # Бизнес-логика
│       ├── receipt_service.py
│       └── income_service.py
├── migrations/             # SQL миграции
├── requirements.txt
├── Dockerfile
└── README.md
```

## API Endpoints

### POST /api/v1/payments
Создание нового платежа.

**Request:**
```json
{
  "user_id": 123456789,
  "vacancy_id": 1,
  "payment_type": "legal_entity",
  "amount": 5000.00,
  "currency": "RUB",
  "company_info": {
    "name": "ООО \"Рога и Копыта\"",
    "inn": "1234567890",
    "kpp": "123456789",
    "legal_address": "г. Москва, ул. Примерная, д. 1",
    "email": "accounting@example.com"
  }
}
```

**Response:**
```json
{
  "payment_id": 1,
  "payment_url": "https://robokassa.com/payment/...",
  "status": "processing",
  "message": "Платеж создан успешно"
}
```

### GET /api/v1/payments/{payment_id}
Получить информацию о платеже.

### POST /api/v1/payments/{payment_id}/receipt
Создать чек самозанятого для платежа.

**Request:**
```json
{
  "client_name": "ООО \"Рога и Копыта\"",
  "client_type": "legal_entity",
  "client_inn": "1234567890",
  "service_name": "Услуги по подбору персонала",
  "email": "accounting@example.com"
}
```

### POST /api/v1/webhooks/robokassa
Webhook от Robokassa для уведомления о статусе платежа.

## Настройка

### Переменные окружения

Создайте файл `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://recruiter:recruiter@postgres:5432/recruiter

# Robokassa
ROBOKASSA_MERCHANT_LOGIN=your_merchant_login
ROBOKASSA_PASSWORD1=password1
ROBOKASSA_PASSWORD2=password2
ROBOKASSA_IS_TEST=true

# Мой налог (самозанятый)
MY_TAX_INN=your_inn
MY_TAX_API_KEY=your_api_key_if_available

# DB Core URL
DB_CORE_URL=http://db-core:8000
```

## Запуск

### Docker Compose

Сервис автоматически запускается через `docker-compose.yml`.

### Локально

```bash
cd payment-gateway
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Интеграция с core-bot

Сервис интегрирован с `core-bot` через `PaymentGatewayClient`. 

Пример использования в `core-bot`:

```python
from payment_gateway_client import get_payment_gateway_client

payment_gateway = get_payment_gateway_client()
payment = await payment_gateway.create_payment(
    user_id=123456789,
    vacancy_id=1,
    payment_type="legal_entity",
    amount=5000.00,
    company_info={
        "name": "ООО \"Рога и Копыта\"",
        "inn": "1234567890",
        "email": "accounting@example.com"
    }
)
```

## Миграции

Применение миграций:

```bash
docker-compose exec postgres psql -U recruiter -d recruiter -f /path/to/migrations/001_create_payment_tables.sql
```

Или через Python:

```python
from app.database import init_db
await init_db()
```

## Статусы платежей

- `pending` - Платеж создан, ожидает оплаты
- `processing` - Платеж обрабатывается
- `completed` - Платеж завершен успешно
- `failed` - Платеж не прошел

## Отслеживание дохода

Сервис автоматически отслеживает:
- Общий доход за год
- Доход от физ. лиц (налог 4%)
- Доход от юр. лиц (налог 6%)
- Превышение лимита 2.4 млн руб/год

