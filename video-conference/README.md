# Video Conference Service

Сервис для видеоконференций с автоматической записью диалогов.

## Возможности

- 🎥 Видеоконференции через WebRTC (P2P)
- 💬 Текстовый чат во время конференции
- 📝 Автоматическая запись всех сообщений и событий
- 💾 Сохранение транскрипций в .txt файлы
- 🔗 Автогенерируемые ссылки для доступа к комнатам
- 📧 Вход по имени и email

## Структура

- `app/` - Backend на FastAPI с WebSocket поддержкой
- `frontend/` - Frontend на React + Vite + Tailwind CSS

## API Endpoints

- `POST /api/rooms/create` - Создать новую комнату (возвращает `room_id`)
- `GET /api/rooms/{room_id}` - Получить информацию о комнате
- `GET /api/rooms/{room_id}/transcript` - Получить транскрипцию
- `POST /api/rooms/{room_id}/save-transcript` - Сохранить транскрипцию в файл
- `WS /ws/{room_id}` - WebSocket для координации видеоконференции

## Использование

1. Создайте комнату через API:
```bash
curl -X POST http://localhost:8004/api/rooms/create
# Ответ: {"room_id": "abc123..."}
```

2. Откройте в браузере:
```
http://localhost:3001/?room=abc123...
```

3. Введите имя и email, затем присоединяйтесь к конференции.

## Запуск

### Docker Compose

Сервис запускается автоматически:
```bash
docker compose up --build video-conference video-conference-frontend
```

### Локально

#### Backend:
```bash
cd video-conference
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8004
```

#### Frontend:
```bash
cd video-conference/frontend
npm install
npm run dev
```

## Порты

- Backend: `8004`
- Frontend: `3001`

