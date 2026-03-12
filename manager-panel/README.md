# Manager Panel

Менеджерская панель для RecruitR - отдельный микросервис для менеджеров, позволяющий управлять кандидатами и планировать созвоны.

## Возможности

- ✅ Авторизация менеджеров по email
- 📋 Список всех кандидатов, обработанных менеджером
- 📄 Просмотр резюме кандидатов
- 📊 Анализ после первичного скрининга
- 🎥 Анализ после второго скрининга (видеоконференция)
- 📅 Календарь для планирования созвонов
- 📈 Статусы кандидатов

## Структура

- `app/` - Backend (FastAPI)
- `frontend/` - Frontend (React + Vite + Tailwind CSS)

## Запуск

```bash
docker compose up manager-panel manager-panel-frontend
```

Сервисы будут доступны:
- Backend API: http://localhost:8005
- Frontend: http://localhost:3002

## API Endpoints

### Авторизация
- `POST /api/auth/login` - Вход по email

### Кандидаты
- `GET /api/candidates` - Список кандидатов менеджера
- `GET /api/candidates/{id}` - Детали кандидата

### Календарь
- `GET /api/calendar/events` - Список событий
- `POST /api/calendar/events` - Создать событие
- `PUT /api/calendar/events/{id}` - Обновить событие
- `DELETE /api/calendar/events/{id}` - Удалить событие

## База данных

Сервис создает таблицу `manager_calendar_events` для хранения событий календаря.

