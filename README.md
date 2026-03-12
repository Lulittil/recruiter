# recruiter
Stack of microservices for HR Bot

## Сервисы

- `hr-bot` — обработка команд по отзыву согласия.
- `OfferAnalyzer` — анализ предложений и подготовка рекомендаций.
- `bot-core` — HTTP/WebSocket фронт для ботов, публикация команд в Kafka.
- `db-core` — REST API для профилей и результатов анализа.
- `admin-panel` — веб-админка для управления вакансиями, кандидатами и менеджерами.
- `payment-gateway` — обработка платежей и генерация чеков.
- `core-bot` — основной Telegram бот.
- `video-conference` — сервис видеоконференций с записью транскрипций.

## Локальный запуск

Каждый сервис содержит собственный `README.md` и `requirements.txt`. Пример запуска:

```bash
cd bot-core
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Аналогично для `db-core`. Для воркеров бот-процессов необходимо настроить доступ к Kafka и базе данных согласно требованиям в `ROADMAP.md`.

## Docker Compose

Для запуска инфраструктуры и основных сервисов используйте:

```bash
docker compose up --build
```

По умолчанию поднимутся `postgres`, `kafka`, `kafka-ui`, `db-core`, `bot-core`, `payment-gateway` и `admin-panel`.  
Чтобы дополнительно запустить воркеры (`hr-bot`, `offer-analyzer`), задайте профиль:

```bash
docker compose --profile workers up --build
```

Перед запуском задайте токены Telegram и другие секреты через переменные окружения (`HR_BOT_TOKEN`, `OFFER_ANALYZER_TOKEN`).

## Веб-сервисы

### Админ-панель

Веб-админка доступна по адресу: http://localhost:3000

**Логин по умолчанию:**
- Username: `admin`
- Password: `admin123`

⚠️ **Важно**: В продакшене обязательно измените дефолтный пароль!

Админка позволяет:
- Управлять вакансиями (создание, редактирование)
- Просматривать кандидатов по вакансиям
- Управлять менеджерами вакансий
- Просматривать статистику

Подробнее см. [admin-panel/README.md](admin-panel/README.md)

### Видеоконференции

Сервис видеоконференций доступен по адресу: http://localhost:3001

**Использование:**
1. Создайте комнату через API: `POST http://localhost:8004/api/rooms/create`
2. Откройте ссылку: `http://localhost:3001/?room=ROOM_ID`
3. Введите имя и email для входа

Подробнее см. [video-conference/README.md](video-conference/README.md)