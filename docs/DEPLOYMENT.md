# 🚀 Deployment Guide

Руководство по развертыванию Firebird DB Proxy API на различных платформах.

## Оглавление

- [Railway.com (рекомендуется)](#railwaycom)
- [Render.com](#rendercom)
- [Heroku](#heroku)
- [Docker](#docker)
- [VPS (ручной deployment)](#vps)

---

## Railway.com

**Рекомендуется** для этого проекта - простота, статический IP, хороший free tier.

### Преимущества

- ✅ Статический IP из коробки
- ✅ Автоматический deploy из GitHub
- ✅ Простая настройка environment variables
- ✅ Хороший free tier
- ✅ Автоматическое обнаружение Dockerfile

### Шаг 1: Подготовка репозитория

```bash
# Инициализация Git
cd firebird-db-proxy
git init
git add .
git commit -m "Initial commit: Firebird DB Proxy API"

# Создать репозиторий на GitHub
# (через GitHub web interface)

# Добавить remote и запушить
git remote add origin https://github.com/YOUR_USERNAME/firebird-db-proxy.git
git branch -M main
git push -u origin main
```

### Шаг 2: Создание проекта на Railway

1. Зайти на https://railway.com/
2. Войти через GitHub
3. Нажать **New Project**
4. Выбрать **Deploy from GitHub repo**
5. Выбрать репозиторий `firebird-db-proxy`
6. Railway автоматически обнаружит Dockerfile и начнет deployment

### Шаг 3: Настройка Environment Variables

В Railway Dashboard → **Variables** → **Raw Editor**:

```env
DB_HOST=your-firebird-host.com
DB_PORT=3050
DB_NAME=YOUR_DATABASE
DB_USER=SYSDBA
DB_PASSWORD=your-secure-password
API_TOKENS=ВАШІ_ЗГЕНЕРОВАНІ_ТОКЕНИ
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
LOG_LEVEL=INFO
APP_ENV=production
ALLOWED_ORIGINS=*
```

**⚠️ ВАЖНО:** Сгенерируйте сильные токены:

```bash
python scripts/generate_token.py --count 2
# Скопировать токены в API_TOKENS через запятую
```

### Шаг 4: Получение статического IP

1. Railway Dashboard → **Settings** → **Networking**
2. Включить **Static Outbound IP**
3. Скопировать IP адрес
4. **КРИТИЧЕСКИ ВАЖНО:** Добавить этот IP в whitelist на Firebird сервере!

### Шаг 5: Настройка домена

Railway автоматически предоставляет домен:

```
https://your-app-name.railway.app
```

Можно подключить свой домен:

1. Railway Dashboard → **Settings** → **Domains**
2. Добавить свой домен
3. Настроить DNS записи у регистратора

### Шаг 6: Проверка deployment

```bash
# Health check
curl https://your-app-name.railway.app/api/health

# Тест API
curl -X POST https://your-app-name.railway.app/api/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT 1 FROM RDB$DATABASE"}'
```

### Мониторинг

Railway Dashboard → **Deployments** → **Logs**

```
[2025-10-21 12:34:56] [INFO] Starting Firebird DB Proxy v1.0.0
[2025-10-21 12:34:56] [INFO] Database: your-host.com/3050:YOUR_DATABASE
[2025-10-21 12:34:56] [INFO] Database connection test: SUCCESS ✓
```

---

## Render.com

Бесплатная альтернатива с автоматическим deployment.

### Шаг 1: Создать проект

1. Зайти на https://render.com/
2. Создать **New Web Service**
3. Подключить GitHub репозиторий

### Шаг 2: Конфигурация

**Build Command:**
```bash
docker build -t firebird-db-proxy .
```

**Start Command:**
```bash
docker run -p 8000:8000 firebird-db-proxy
```

**Environment Variables:**
```env
DB_HOST=85.114.224.45
DB_PORT=3055
DB_NAME=DK_GEORGIA
DB_USER=SYSDBA
DB_PASSWORD=masterkey
API_TOKENS=your-tokens
LOG_LEVEL=INFO
```

### Шаг 3: Статический IP

⚠️ Render не предоставляет статический IP в free tier.

Решение:
- Использовать Render + CloudFlare для статического IP
- Перейти на платный план ($7/месяц)

---

## Heroku

Классическая платформа (требует кредитную карту).

### Шаг 1: Установка Heroku CLI

```bash
# Windows
choco install heroku-cli

# Mac
brew install heroku/brew/heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### Шаг 2: Логин и создание приложения

```bash
heroku login
heroku create firebird-db-proxy

# Установить stack на container (для Docker)
heroku stack:set container -a firebird-db-proxy
```

### Шаг 3: Настройка environment variables

```bash
heroku config:set -a firebird-db-proxy \
  DB_HOST=your-firebird-host.com \
  DB_PORT=3050 \
  DB_NAME=YOUR_DATABASE \
  DB_USER=SYSDBA \
  DB_PASSWORD=your-secure-password \
  API_TOKENS=your-tokens \
  LOG_LEVEL=INFO
```

### Шаг 4: Deploy

```bash
git push heroku main
```

### Шаг 5: Статический IP

```bash
# Требует платный dyno ($25/месяц)
heroku addons:create static-ip -a firebird-db-proxy
```

---

## Docker

Локальный запуск через Docker.

### Сборка образа

```bash
docker build -t firebird-db-proxy .
```

### Запуск контейнера

```bash
docker run -d \
  --name firebird-db-proxy \
  -p 8000:8000 \
  -e DB_HOST=your-firebird-host.com \
  -e DB_PORT=3050 \
  -e DB_NAME=YOUR_DATABASE \
  -e DB_USER=SYSDBA \
  -e DB_PASSWORD=your-secure-password \
  -e API_TOKENS=your-token \
  -e LOG_LEVEL=INFO \
  firebird-db-proxy
```

### Или через .env файл

```bash
docker run -d \
  --name firebird-db-proxy \
  -p 8000:8000 \
  --env-file .env \
  firebird-db-proxy
```

### Проверка

```bash
# Логи
docker logs -f firebird-db-proxy

# Health check
curl http://localhost:8000/api/health
```

### Docker Compose (опционально)

Создать `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Запуск:

```bash
docker-compose up -d
```

---

## VPS

Ручной deployment на виртуальном сервере.

### Требования

- Ubuntu 20.04+
- Python 3.11+
- Nginx (для reverse proxy)
- Systemd (для автозапуска)

### Шаг 1: Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y python3.11 python3.11-venv python3-pip nginx

# Создать пользователя для приложения
sudo useradd -m -s /bin/bash appuser
```

### Шаг 2: Установка приложения

```bash
# Переключиться на appuser
sudo su - appuser

# Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/firebird-db-proxy.git
cd firebird-db-proxy

# Создать виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env
nano .env  # Заполнить параметры
```

### Шаг 3: Systemd service

Создать `/etc/systemd/system/firebird-db-proxy.service`:

```ini
[Unit]
Description=Firebird DB Proxy API
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/home/appuser/firebird-db-proxy
Environment="PATH=/home/appuser/firebird-db-proxy/venv/bin"
ExecStart=/home/appuser/firebird-db-proxy/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Запуск сервиса:

```bash
sudo systemctl daemon-reload
sudo systemctl enable firebird-db-proxy
sudo systemctl start firebird-db-proxy
sudo systemctl status firebird-db-proxy
```

### Шаг 4: Nginx reverse proxy

Создать `/etc/nginx/sites-available/firebird-db-proxy`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активировать конфиг:

```bash
sudo ln -s /etc/nginx/sites-available/firebird-db-proxy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Шаг 5: SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Мониторинг

```bash
# Логи приложения
sudo journalctl -u firebird-db-proxy -f

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Checklist после deployment

- [ ] API доступен по URL
- [ ] Health check возвращает `200 OK`
- [ ] База данных подключена (database_connected: true)
- [ ] Токен аутентификации работает
- [ ] SQL запросы выполняются
- [ ] Статический IP получен
- [ ] IP добавлен в whitelist Firebird сервера
- [ ] HTTPS настроен (для production)
- [ ] Логи пишутся корректно
- [ ] Мониторинг настроен

---

## Troubleshooting

### Проблема: База данных не подключается

**Симптомы:**
```json
{"database_connected": false}
```

**Решения:**
1. Проверить параметры подключения в `.env`
2. Проверить что IP добавлен в whitelist на Firebird сервере
3. Проверить доступность порта:
   ```bash
   telnet your-firebird-host.com 3050
   ```

### Проблема: 401 Unauthorized

**Решения:**
1. Проверить токен в заголовке Authorization
2. Проверить `API_TOKENS` в environment variables
3. Убедиться что токен не содержит лишних пробелов

### Проблема: 429 Too Many Requests

**Решения:**
1. Увеличить лимиты через environment variables:
   ```env
   RATE_LIMIT_PER_MINUTE=120
   RATE_LIMIT_PER_HOUR=2000
   ```

### Проблема: Медленные запросы

**Решения:**
1. Увеличить `DB_MAX_CONNECTIONS`
2. Оптимизировать SQL запросы (индексы в БД)
3. Увеличить количество workers:
   ```bash
   uvicorn app.main:app --workers 4
   ```

---

**Версия:** 1.0.0  
**Последнее обновление:** 2025-10-21

