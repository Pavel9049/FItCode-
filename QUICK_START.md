# 🚀 Быстрый старт FitCoach Bot

## ⚡ Запуск за 5 минут

### 1. Подготовка окружения

```bash
# Клонирование репозитория (если еще не сделано)
git clone <repository-url>
cd fitcoach-bot

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка конфигурации

```bash
# Копирование файла конфигурации
cp .env.example .env

# Редактирование конфигурации
nano .env  # или любой текстовый редактор
```

**Обязательные настройки в .env:**
```env
# Токен вашего бота (получите у @BotFather)
TELEGRAM_BOT_TOKEN=8269244638:AAHbZ8O3eJ6dt-SRmsdnP_bQ9XTn0zxScY

# Режим работы (polling для разработки)
RUN_MODE=polling

# База данных (SQLite для быстрого старта)
DATABASE_URL=sqlite:///dev.db
```

### 3. Инициализация базы данных

```bash
# Создание таблиц в базе данных
python -c "from app.db.session import init_db; import asyncio; asyncio.run(init_db())"
```

### 4. Запуск бота

```bash
# Запуск в режиме polling
python app/main.py
```

**Или через модуль:**
```bash
python -m app.main
```

### 5. Проверка работы

1. Откройте Telegram
2. Найдите вашего бота по токену
3. Отправьте команду `/start`
4. Проверьте все разделы меню

## 🎯 Основные команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу с ботом |
| `/cabinet` | Личный кабинет |
| `/workouts` | Тренировки |
| `/menu` | Меню на неделю |
| `/kbju` | AI КБЖУ по фото |
| `/rewards` | Звезды и призы |
| `/settings` | Настройки |
| `/instagram` | Instagram |
| `/ref` | Реферальная ссылка |
| `/support` | Поддержка |

## 🔧 Настройка для продакшена

### 1. Настройка webhook

```bash
# Измените в .env
RUN_MODE=webhook
WEBHOOK_BASE_URL=https://your-domain.com

# Установите webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/webhook/telegram"}'
```

### 2. Настройка PostgreSQL

```bash
# Установка PostgreSQL
sudo apt install postgresql postgresql-contrib

# Создание базы данных
sudo -u postgres psql
CREATE DATABASE fitcoach;
CREATE USER fitcoach WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fitcoach TO fitcoach;
\q

# Обновите DATABASE_URL в .env
DATABASE_URL=postgresql+asyncpg://fitcoach:your_password@localhost:5432/fitcoach
```

### 3. Настройка systemd

```bash
# Создание сервиса
sudo nano /etc/systemd/system/fitcoach-bot.service
```

```ini
[Unit]
Description=FitCoach Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/fitcoach-bot
Environment=PATH=/path/to/fitcoach-bot/venv/bin
ExecStart=/path/to/fitcoach-bot/venv/bin/python app/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Включение и запуск
sudo systemctl daemon-reload
sudo systemctl enable fitcoach-bot
sudo systemctl start fitcoach-bot
```

## 🐳 Запуск через Docker

### 1. Создание docker-compose.yml

```yaml
version: '3.8'
services:
  bot:
    build: .
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - DATABASE_URL=sqlite:///dev.db
      - RUN_MODE=polling
    volumes:
      - ./dev.db:/app/dev.db
    ports:
      - "8080:8080"
```

### 2. Запуск

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot
```

## 🔍 Отладка

### Просмотр логов

```bash
# Логи бота
tail -f bot.log

# Логи systemd
sudo journalctl -u fitcoach-bot -f

# Логи Docker
docker-compose logs -f bot
```

### Проверка статуса

```bash
# Статус сервиса
sudo systemctl status fitcoach-bot

# Проверка портов
netstat -tulpn | grep :8080

# Проверка процессов
ps aux | grep python
```

### Частые проблемы

#### 1. Ошибка "ModuleNotFoundError"
```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Переустановите зависимости
pip install -r requirements.txt
```

#### 2. Ошибка "Database connection failed"
```bash
# Проверьте DATABASE_URL в .env
# Для SQLite убедитесь, что файл доступен для записи
chmod 666 dev.db
```

#### 3. Ошибка "Invalid token"
```bash
# Проверьте токен в .env
# Получите новый токен у @BotFather
```

#### 4. Бот не отвечает
```bash
# Проверьте режим работы (polling/webhook)
# Проверьте логи на ошибки
# Убедитесь, что бот не заблокирован
```

## 📊 Мониторинг

### Основные метрики

```bash
# Количество пользователей
sqlite3 dev.db "SELECT COUNT(*) FROM users;"

# Количество покупок
sqlite3 dev.db "SELECT COUNT(*) FROM purchases WHERE paid = 1;"

# Активность за последние 24 часа
sqlite3 dev.db "SELECT COUNT(*) FROM users WHERE created_at > datetime('now', '-1 day');"
```

### Проверка здоровья

```bash
# Проверка API
curl http://localhost:8080/health

# Проверка базы данных
python -c "from app.db.session import get_session_maker; import asyncio; asyncio.run(get_session_maker())"
```

## 🎉 Поздравляем!

Ваш FitCoach Bot успешно запущен! 

### Что дальше?

1. **Протестируйте все функции** бота
2. **Настройте платежные системы** для приема оплаты
3. **Добавьте контент**: видео упражнений, фото блюд
4. **Настройте мониторинг** и логирование
5. **Разверните в продакшене** с SSL и доменом

### Полезные ссылки

- 📖 [Полная документация](README.md)
- 🚀 [Инструкции по развертыванию](DEPLOYMENT.md)
- 📋 [Журнал изменений](CHANGELOG.md)
- ⚙️ [Конфигурация](.env.example)

### Поддержка

- 💬 Telegram: @fitcoach_support
- 📧 Email: support@fitcoach.com
- 🌐 Website: https://fitcoach.com

---

**Удачного использования FitCoach Bot!** 💪