# FitCoach Bot (Telegram)

Полностью автоматизированный Telegram-бот для фитнеса и здорового питания: платные программы, персонализация, мотивационная система, AI-оценка КБЖУ по фото, интеграция с Instagram, админ-панель и рассылки.

## Стек
- Python 3.11+
- aiogram v3
- FastAPI (вебхуки и внешние интеграции)
- PostgreSQL (SQLAlchemy)
- APScheduler (рассылки и cron)
- Stripe, ЮKassa, Telegram Stars (оплаты)
- Google Vision API (AI по фото)
- Docker + docker-compose

## Быстрый старт (локально, polling)
1. Установите зависимости:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
2. Скопируйте `.env.example` в `.env` и заполните переменные.
3. Запустите Postgres (локально или через docker-compose).
4. Запуск бота (polling + FastAPI веб-сервер):
```bash
python -m app.main
```

## Продакшен (webhook)
- Рекомендуется Render/VPS.
- Установите `WEBHOOK_BASE_URL` и включите `RUN_MODE=webhook`.
- Пробросьте 443/80/8080 и настройте SSL (через прокси, например, Caddy/NGINX/Cloudflare Tunnel).

## Переменные окружения
См. `.env.example` для полного списка. Критичные:
- TELEGRAM_BOT_TOKEN
- DATABASE_URL (например: postgresql+asyncpg://user:pass@host:5432/db)
- STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET
- YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY
- GOOGLE_APPLICATION_CREDENTIALS (путь к JSON ключу Vision API)
- SUPPORT_CHAT_ID (ID группы поддержки)

## Структура проекта (основное)
```
app/
  main.py                # запуск бота + веб-сервера
  config.py              # конфигурация из .env
  db/
    session.py           # подключение к БД
    models.py            # модели SQLAlchemy
  routers/               # хэндлеры aiogram
  services/              # бизнес-логика (оплаты, AI, планы и т.д.)
  web/                   # FastAPI-приложение (вебхуки, API)
  background/            # планировщик (APScheduler)
```

## Миграции
Для простоты разработки таблицы создаются автоматически при первом запуске. В проде используйте Alembic.

## Контент
- Видео упражнений: храните ссылки на YouTube (Unlisted) или Telegram.
- Баннер/видео для приветствия положите в `assets/banner.*` (опционально).

## Лицензии и ответственность
- Убедитесь, что у вас есть права на весь контент (упражнения, фото, рецепты, видео).
- Бот не заменяет консультацию врача. Используйте на свой риск.

## Поддержка
- PRO-подписчики могут писать в чат поддержки (форвардинг в группу `SUPPORT_CHAT_ID`).
