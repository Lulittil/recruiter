# db-core

Заготовка сервиса хранения данных с REST API на FastAPI и SQLAlchemy.

## Запуск

```bash
uvicorn app.main:app --reload
```

## Переменные окружения

- `DATABASE_URL` — строка подключения к базе данных (по умолчанию `sqlite+aiosqlite:///./db.sqlite3`).

## Основные компоненты

- `app.main` — FastAPI-приложение с CRUD-заглушками.
- `app.database` — конфигурация SQLAlchemy и зависимость сессии.
- `app.models` — ORM-модели.
- `app.schemas` — pydantic-схемы для обмена данными.

## TODO

- Настроить реальные модели и миграции (alembic).
- Добавить авторизацию и валидацию сервисных токенов.
- Реализовать запросы, используемые `hr-bot` и `offerAnalyzer`.

