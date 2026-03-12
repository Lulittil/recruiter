# Core Bot

Telegram бот для управления настройками вакансий и ботов, а также обработки платежей.

## Функциональность

- Создание и управление вакансиями
- Добавление/удаление менеджеров
- Настройка стратегий распределения кандидатов
- Оплата через Telegram Payments
- Просмотр статистики

## Настройка

1. Скопируйте файл `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Заполните переменные окружения в `.env`:

### Переменные окружения

- `CORE_BOT_TOKEN` - Токен Telegram бота (обязательно)
  - Получить у [@BotFather](https://t.me/BotFather) в Telegram
  - Создайте нового бота командой `/newbot` и скопируйте токен

- `DB_CORE_URL` - URL сервиса db-core (по умолчанию: http://db-core:8000)
  - Для локальной разработки можно использовать: http://localhost:8000

- `PAYMENT_PROVIDER_TOKEN` - Токен провайдера платежей Telegram (опционально)
  - Получить у [@BotFather](https://t.me/BotFather) для включения платежей
  - Инструкция:
    1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
    2. Отправьте команду `/mybots`
    3. Выберите вашего бота
    4. Выберите "Payments" → "Payment Provider"
    5. Следуйте инструкциям для настройки провайдера платежей
    6. После настройки BotFather выдаст токен вида: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
  - **Важно**: Токены для платежей выдаются только через @BotFather, их нельзя сгенерировать самостоятельно
  - Для тестирования используйте `IS_TEST=true` (токен не требуется)

- `ADMIN_CHAT_IDS` - Список chat ID администраторов через запятую (опционально)
  - Пример: `ADMIN_CHAT_IDS=123456789,987654321`
  - Узнать свой chat_id можно через бота [@userinfobot](https://t.me/userinfobot)

## Запуск

### Локально

```bash
python main.py
```

### Docker

```bash
docker build -t core-bot .
docker run --env-file .env core-bot
```

### Docker Compose

```bash
docker-compose up core-bot
```

Убедитесь, что переменные окружения установлены в `.env` файле в корне проекта или переданы через `docker-compose.yml`.

