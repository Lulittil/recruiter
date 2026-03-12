# Admin Panel - Веб-админка для RecruitR

Красивая веб-админка для управления вакансиями, кандидатами и менеджерами.

## Возможности

- 🔐 **Авторизация** - JWT токены, безопасная система входа
- 📊 **Дашборд** - Общая статистика по вакансиям и кандидатам
- 💼 **Управление вакансиями** - Создание, редактирование, просмотр вакансий
- 👥 **Управление кандидатами** - Просмотр списка кандидатов по вакансиям
- ⚙️ **Управление менеджерами** - Добавление и удаление менеджеров из вакансий
- 🎨 **Красивый UI** - Современный интерфейс на React + Tailwind CSS

## Структура

- `app/` - Backend на FastAPI
- `frontend/` - Frontend на React + Vite + Tailwind CSS

## Запуск

### Локально (для разработки)

#### Backend:
```bash
cd admin-panel
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

#### Frontend:
```bash
cd admin-panel/frontend
npm install
npm run dev
```

### В Docker

Админка автоматически запускается через Docker Compose:

```bash
docker compose up --build admin-panel admin-panel-frontend
```

## Доступ

- **URL**: http://localhost:3000
- **Логин по умолчанию**: `admin`
- **Пароль по умолчанию**: `admin123`

⚠️ **Важно**: В продакшене обязательно измените дефолтный пароль и SECRET_KEY!

## API Endpoints

Все API endpoints требуют авторизации (JWT токен):

- `POST /api/auth/login` - Вход в систему
- `GET /api/auth/me` - Информация о текущем пользователе
- `GET /api/vacancies` - Список вакансий
- `POST /api/vacancies` - Создать вакансию
- `GET /api/vacancies/{id}` - Получить вакансию
- `PUT /api/vacancies/{id}` - Обновить вакансию
- `GET /api/vacancies/{id}/applicants` - Кандидаты по вакансии
- `GET /api/vacancies/{id}/managers` - Менеджеры по вакансии
- `POST /api/vacancies/{id}/managers` - Добавить менеджера
- `DELETE /api/vacancies/{id}/managers/{manager_id}` - Удалить менеджера

## Технологии

**Backend:**
- FastAPI
- Python JWT (jose)
- Passlib для хэширования паролей
- httpx для HTTP клиента

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- React Router
- Axios
- Lucide React (иконки)

