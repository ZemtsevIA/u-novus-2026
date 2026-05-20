# Skill Assessment Telegram Bot

MVP Telegram-бота для первичной оценки навыков пользователя. Бот задает вопросы по выбранной теме, сохраняет ответы в PostgreSQL, получает моковый результат от слоя нейронки и открывает доступ к Telegram Mini App после подтверждения или ручного выбора уровня.

## Стек

- Python 3.12+
- FastAPI
- aiogram 3.x
- SQLAlchemy 2.x async
- Alembic
- PostgreSQL
- Pydantic v2 / pydantic-settings
- httpx

## Быстрый старт локально

1. Создайте окружение и установите зависимости:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Создайте `.env` для локального polling-режима:

```bash
cp .env.local.example .env
```

3. Укажите настоящий `BOT_TOKEN` и при необходимости измените `DATABASE_URL`, `MINI_APP_URL`.

4. Поднимите PostgreSQL и примените миграции:

```bash
alembic upgrade head
```

5. Запустите сервис:

```bash
uvicorn app.main:app --reload
```

Для локального запуска используйте `RUN_POLLING=true`: бот сам будет забирать сообщения из Telegram. Healthcheck доступен на `GET /health`.

## Запуск через Docker

```bash
cp .env.local.example .env
docker compose up --build
```

Контейнер `bot_app` применит миграции и запустит FastAPI. При `RUN_POLLING=true` бот будет работать локально через polling.
В Docker Compose `DATABASE_URL` переопределяется автоматически на `postgresql+asyncpg://postgres:postgres@postgres:5432/skill_bot`, потому что база доступна внутри compose-сети по имени сервиса `postgres`.

## Webhook

Webhook-ручка уже подготовлена:

```text
POST /telegram/webhook
```

Для серверного запуска укажите публичный HTTPS-адрес:

```env
RUN_POLLING=false
WEBHOOK_URL=https://your-domain.com/telegram/webhook
```

FastAPI должен быть доступен снаружи по этому адресу. Обычно перед `uvicorn` ставят Nginx/Caddy/Traefik, который принимает HTTPS и проксирует запросы на порт приложения.

Для локальной разработки без публичного HTTPS можно временно включить polling:

```env
RUN_POLLING=true
```

## Мок нейронки

Моковый сервис находится в [app/services/neural_api.py](app/services/neural_api.py). Он реализует тот же интерфейс, что и будущий HTTP-клиент:

- `generate_questions`
- `analyze_answers`
- `send_user_confirmation`
- `generate_roadmap`
- `correct_roadmap`
- `send_roadmap_feedback`

Пока `USE_MOCK_NEURAL_API=true`, используется `MockNeuralApiService`. Чтобы подключить реальный API, установите:

```env
NEURAL_API_BASE_URL=http://157.22.176.60:8000
NEURAL_API_SSL_VERIFY=false
NEURAL_SURVEY_API_ENABLED=true
NEURAL_SURVEY_USE_LLM=false
NEURAL_ASSESSMENT_API_ENABLED=false
NEURAL_API_ERROR_LOG_PATH=logs/neural_api_errors.log
USE_MOCK_NEURAL_API=false
```

HTTP-реализация использует `httpx`. Roadmap-ручки взяты из [README_neuro.md](README_neuro.md):

- `POST /api/survey/questions`
- `POST /api/survey/submit`
- `POST /analyze_answers`
- `POST /confirm_assessment`
- `POST /api/roadmap/remote-rag`
- `POST /api/roadmap/correct`

Вопросы анкеты берутся из `/api/survey/questions`, если `NEURAL_SURVEY_API_ENABLED=true`. Флаг `NEURAL_SURVEY_USE_LLM=false` передаётся в API как `"use_llm": false`, чтобы ручка работала быстро и без YandexGPT-ключей.

Характеристика пользователя берётся из `/api/survey/submit`: бот отправляет ответы по `id` вопроса и получает `profile + search_params`. `profile` показывается пользователю как результат анкеты, а `search_params` сохраняется в оценку и затем используется при запросе роадмапа.

Подтверждение уровня пока остаётся fallback при `NEURAL_ASSESSMENT_API_ENABLED=false`. Когда на neural API появится ручка `/confirm_assessment`, включите `NEURAL_ASSESSMENT_API_ENABLED=true`.

Ошибки связи с neural API пишутся отдельно в `logs/neural_api_errors.log`. В Docker папка `./logs` примонтирована в контейнер, поэтому файл доступен на хосте без `docker logs`.

Контракт по данным:

- `POST /api/survey/questions` получает тему пользователя:

```json
{
  "topic": "Python backend",
  "use_llm": false
}
```

- `POST /api/survey/submit` получает ответы анкеты:

```json
{
  "topic": "Python backend",
  "answers": {
    "current_level": "новичок",
    "time_per_week": "4–6 часов"
  },
  "use_llm": false
}
```

- `POST /analyze_answers` получает тему и выбранные ответы вместе с текстами вопросов:

```json
{
  "telegram_user_id": 123456789,
  "topic": "Python backend",
  "answers": [
    {
      "question": "Есть ли у вас опыт программирования?",
      "answer": "Немного"
    }
  ]
}
```

- `POST /api/roadmap/remote-rag` получает тему, предпочтения, уровень и лимит:

```json
{
  "topic": "Python backend",
  "preferences": "Пользователь хочет изучить: Python backend",
  "level": "новичок",
  "limit": 40,
  "refine_with_llm": true
}
```

- `POST /api/roadmap/correct` получает текущий roadmap, прежние `courses[]` и причину отказа:

```json
{
  "profile": {
    "goal": "Python backend",
    "domain": "IT",
    "level": "новичок",
    "time_per_week": "5-7 часов",
    "format_pref": "любой",
    "career_goal": null
  },
  "current_roadmap": {
    "summary": "Маршрут от нуля до Junior Python Backend Developer",
    "steps": []
  },
  "feedback": "wrong_format",
  "courses": []
}
```

## Основной сценарий

1. `/start`
2. Пользователь нажимает `Пройти оценку`.
3. Вводит тему обучения.
4. Бот получает вопросы от мокового сервиса.
5. Вопросы задаются по одному, ответы принимаются только inline-кнопками.
6. Ответы сохраняются в таблицу `assessment_questions`.
7. После последнего ответа бот получает уровень `beginner`, `middle` или `experienced`.
8. Пользователь подтверждает результат или выбирает уровень вручную.
9. `miniapp_available` становится `true`.
10. Появляются кнопки `Открыть обучение` и `Мой уровень`.

## Структура

```text
app/
  main.py
  core/
  bot/
  api/
  db/
  schemas/
  services/
migrations/
```

Бизнес-логика сценария находится в [app/services/assessment_service.py](app/services/assessment_service.py), работа с внешней нейронкой в [app/services/neural_api.py](app/services/neural_api.py), обработчики aiogram в [app/bot/handlers](app/bot/handlers).
