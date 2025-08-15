# 🚀 Инструкции по развертыванию FitCoach Bot

## 📋 Предварительные требования

### Системные требования
- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: минимум 1GB, рекомендуется 2GB+
- **CPU**: 1 ядро, рекомендуется 2 ядра
- **Диск**: минимум 10GB свободного места
- **Python**: 3.8+

### Необходимые сервисы
- **PostgreSQL** 12+ или **SQLite** (для разработки)
- **Redis** (опционально, для кэширования)
- **Nginx** (для продакшена)
- **SSL сертификат** (Let's Encrypt)

## 🐳 Развертывание через Docker (рекомендуется)

### 1. Подготовка файлов

Создайте `docker-compose.yml`:
```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - DATABASE_URL=postgresql+asyncpg://fitcoach:password@postgres:5432/fitcoach
      - REDIS_URL=redis://redis:6379
      - STRIPE_API_KEY=${STRIPE_API_KEY}
      - STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
      - YOOKASSA_SHOP_ID=${YOOKASSA_SHOP_ID}
      - YOOKASSA_SECRET_KEY=${YOOKASSA_SECRET_KEY}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
      - RUN_MODE=webhook
      - WEBHOOK_BASE_URL=https://your-domain.com
      - SCHEDULER_ENABLED=true
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - ./assets:/app/assets
    depends_on:
      - postgres
      - redis
    ports:
      - "8080:8080"

  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=fitcoach
      - POSTGRES_USER=fitcoach
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - bot

volumes:
  postgres_data:
  redis_data:
```

Создайте `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание пользователя для безопасности
RUN useradd -m -u 1000 bot && chown -R bot:bot /app
USER bot

# Запуск приложения
CMD ["uvicorn", "app.main:create_fastapi_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
```

Создайте `nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream bot {
        server bot:8080;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://bot;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 2. Настройка SSL сертификата

```bash
# Установка Certbot
sudo apt install certbot

# Получение сертификата
sudo certbot certonly --standalone -d your-domain.com

# Копирование сертификатов
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown -R $USER:$USER ssl
```

### 3. Запуск

```bash
# Создание .env файла
cp .env.example .env
# Отредактируйте .env файл

# Запуск сервисов
docker-compose up -d

# Проверка логов
docker-compose logs -f bot
```

## 🖥️ Развертывание на VPS

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx certbot python3-certbot-nginx git

# Создание пользователя для бота
sudo useradd -m -s /bin/bash bot
sudo usermod -aG sudo bot
```

### 2. Настройка PostgreSQL

```bash
# Переключение на пользователя postgres
sudo -u postgres psql

# Создание базы данных и пользователя
CREATE DATABASE fitcoach;
CREATE USER fitcoach WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE fitcoach TO fitcoach;
\q

# Включение автозапуска
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 3. Настройка Redis

```bash
# Редактирование конфигурации
sudo nano /etc/redis/redis.conf

# Добавьте или измените:
bind 127.0.0.1
maxmemory 256mb
maxmemory-policy allkeys-lru

# Перезапуск Redis
sudo systemctl restart redis
sudo systemctl enable redis
```

### 4. Развертывание приложения

```bash
# Переключение на пользователя bot
sudo su - bot

# Клонирование репозитория
git clone <repository-url> fitcoach-bot
cd fitcoach-bot

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cp .env.example .env
nano .env
```

### 5. Настройка systemd

Создайте файл `/etc/systemd/system/fitcoach-bot.service`:
```ini
[Unit]
Description=FitCoach Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=bot
WorkingDirectory=/home/bot/fitcoach-bot
Environment=PATH=/home/bot/fitcoach-bot/venv/bin
ExecStart=/home/bot/fitcoach-bot/venv/bin/uvicorn app.main:create_fastapi_app --factory --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Включение и запуск сервиса
sudo systemctl daemon-reload
sudo systemctl enable fitcoach-bot
sudo systemctl start fitcoach-bot

# Проверка статуса
sudo systemctl status fitcoach-bot
```

### 6. Настройка Nginx

Создайте файл `/etc/nginx/sites-available/fitcoach-bot`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Активация сайта
sudo ln -s /etc/nginx/sites-available/fitcoach-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com
```

## 🔧 Настройка webhook

После развертывания настройте webhook для бота:

```bash
# Установка webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/webhook/telegram"}'
```

## 📊 Мониторинг

### Логирование

```bash
# Просмотр логов бота
sudo journalctl -u fitcoach-bot -f

# Просмотр логов Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Просмотр логов PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Метрики

Создайте скрипт для мониторинга:
```bash
#!/bin/bash
# /home/bot/monitor.sh

# Проверка статуса сервисов
echo "=== Service Status ==="
sudo systemctl status fitcoach-bot --no-pager
sudo systemctl status postgresql --no-pager
sudo systemctl status redis --no-pager
sudo systemctl status nginx --no-pager

# Использование диска
echo "=== Disk Usage ==="
df -h

# Использование памяти
echo "=== Memory Usage ==="
free -h

# Активные соединения
echo "=== Active Connections ==="
netstat -tulpn | grep :8080
```

## 🔒 Безопасность

### Firewall

```bash
# Установка UFW
sudo apt install ufw

# Настройка правил
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Обновления

```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📈 Масштабирование

### Горизонтальное масштабирование

Для увеличения нагрузки используйте:
- **Load Balancer** (HAProxy, Nginx)
- **Кластеризация Redis**
- **Репликация PostgreSQL**
- **Микросервисная архитектура**

### Вертикальное масштабирование

Увеличьте ресурсы сервера:
- **RAM**: до 8GB+
- **CPU**: до 4 ядер+
- **SSD**: до 100GB+
- **Сеть**: до 1Gbps+

## 🚨 Резервное копирование

### Автоматические бэкапы

Создайте скрипт `/home/bot/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/home/bot/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

# Бэкап базы данных
pg_dump -h localhost -U fitcoach fitcoach > $BACKUP_DIR/db_$DATE.sql

# Бэкап файлов приложения
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /home/bot/fitcoach-bot

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

```bash
# Добавление в cron
crontab -e

# Добавьте строку для ежедневного бэкапа в 2:00
0 2 * * * /home/bot/backup.sh
```

## 🔄 Обновления

### Автоматические обновления

Создайте скрипт `/home/bot/update.sh`:
```bash
#!/bin/bash

cd /home/bot/fitcoach-bot

# Остановка сервиса
sudo systemctl stop fitcoach-bot

# Обновление кода
git pull origin main

# Активация виртуального окружения
source venv/bin/activate

# Обновление зависимостей
pip install -r requirements.txt

# Применение миграций (если используется Alembic)
# alembic upgrade head

# Запуск сервиса
sudo systemctl start fitcoach-bot

# Проверка статуса
sudo systemctl status fitcoach-bot
```

## 📞 Поддержка

### Полезные команды

```bash
# Перезапуск всех сервисов
sudo systemctl restart fitcoach-bot postgresql redis nginx

# Проверка конфигурации Nginx
sudo nginx -t

# Проверка статуса SSL сертификата
sudo certbot certificates

# Просмотр использования ресурсов
htop
iotop
```

### Контакты для поддержки
- **Email**: support@fitcoach.com
- **Telegram**: @fitcoach_support
- **Документация**: https://docs.fitcoach.com

---

**Успешного развертывания!** 🚀