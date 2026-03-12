# bot-core

Заготовка микросервиса, принимающего команды от клиентов и публикующего события в Kafka.

## Запуск

```bash
uvicorn app.main:app --reload
```

## Переменные окружения

- `KAFKA_BOOTSTRAP_SERVERS` — список брокеров Kafka (по умолчанию `localhost:9092`).
- `COMMANDS_TOPIC` — топик для исходящих команд (`bot.commands`).
- `STATUS_TOPIC` — топик для входящих событий (`bot.status`).

## Основные компоненты

- `app.main` — точка входа FastAPI c HTTP и WebSocket обработчиками.
- `app.producer` — заглушка продюсера Kafka.
- `app.schemas` — pydantic-схемы для команд.

## TODO

- Реализовать фактический продюсер/консьюмер Kafka (aiokafka).
- Добавить хранение сессий, авторизацию и логирование.
- Интегрировать с `db-core` и обработчиками команд.

