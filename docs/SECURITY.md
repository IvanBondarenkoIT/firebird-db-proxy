# 🔒 Security Guide

Руководство по безопасности Firebird Database Proxy API.

## Оглавление

- [Обзор безопасности](#обзор-безопасности)
- [Аутентификация](#аутентификация)
- [SQL Injection защита](#sql-injection-защита)
- [Rate Limiting](#rate-limiting)
- [HTTPS](#https)
- [Environment Variables](#environment-variables)
- [Best Practices](#best-practices)
- [Аудит безопасности](#аудит-безопасности)

---

## Обзор безопасности

### Уровни защиты

1. **Network Level**
   - Статический IP в whitelist Firebird сервера
   - HTTPS только в production
   - CORS настройка

2. **Application Level**
   - Bearer Token аутентификация
   - SQL запросов валидация
   - Rate limiting
   - Логирование всех операций

3. **Database Level**
   - READ-ONLY операции
   - Параметризованные запросы
   - Connection pooling

---

## Аутентификация

### Bearer Token

API использует Bearer Token схему аутентификации.

#### Генерация сильных токенов

```bash
# Генерация криптографически безопасного токена
python scripts/generate_token.py --length 64

# Результат:
# Token 1: a1b2c3d4e5f6...64 символа
```

#### Требования к токенам

✅ **Хорошие токены:**
- Минимум 32 байта (64 hex символа)
- Криптографически случайные
- Уникальные для каждого клиента

❌ **Плохие токены:**
```
my-token          # Слишком короткий
password123       # Предсказуемый
token-1           # Неслучайный
```

#### Хранение токенов

**Сервер:**
```env
# .env файл (НЕ коммитить в Git!)
API_TOKENS=a1b2c3d4...,e5f6g7h8...
```

**Клиент:**
```python
# config.py или environment variables
API_TOKEN = os.getenv("FIREBIRD_API_TOKEN")

# НЕ хардкодить в коде!
# API_TOKEN = "hardcoded-token"  # ❌ НИКОГДА!
```

#### Ротация токенов

Рекомендуется периодически менять токены:

1. Сгенерировать новый токен
2. Добавить новый токен в `API_TOKENS` (через запятую)
3. Обновить клиенты на новый токен
4. Удалить старый токен из `API_TOKENS`

```env
# Старый токен
API_TOKENS=old-token

# Переходный период (оба работают)
API_TOKENS=old-token,new-token

# Только новый токен
API_TOKENS=new-token
```

### Множественные токены

Разные токены для разных клиентов/приложений:

```env
API_TOKENS=mobile-app-token,web-app-token,analytics-token
```

Преимущества:
- Можно отозвать доступ конкретного клиента
- Логирование по токенам
- Разные rate limits (в будущем)

---

## SQL Injection защита

### Многоуровневая защита

#### 1. Валидация запросов

```python
# app/validators.py
FORBIDDEN_PATTERNS = [
    r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b',
    r'\b(EXECUTE\s+BLOCK)\b',
    r'\b(EXECUTE\s+PROCEDURE)\b',
    r';.*;\s*',  # Множественные запросы
]
```

#### 2. Параметризованные запросы

✅ **Безопасно:**
```python
# Параметры передаются отдельно
query = "SELECT * FROM STORGRP WHERE ID = ?"
params = [user_input]
db.execute_query(query, params)
```

❌ **Небезопасно:**
```python
# Никогда не делайте так!
query = f"SELECT * FROM STORGRP WHERE ID = {user_input}"
db.execute_query(query)
```

#### 3. Удаление комментариев

SQL комментарии удаляются перед проверкой:

```python
# Попытка обхода через комментарии
"SELECT * FROM STORGRP /* */ UPDATE /* hack */"
# ↓ После удаления комментариев ↓
"SELECT * FROM STORGRP  UPDATE  "
# ↓ Блокируется валидатором ✗
```

### Разрешенные операции

✅ **Только READ-ONLY:**
- `SELECT`
- `WITH` (CTE)

❌ **Все остальное заблокировано:**
- DML: `INSERT`, `UPDATE`, `DELETE`
- DDL: `CREATE`, `DROP`, `ALTER`, `TRUNCATE`
- DCL: `GRANT`, `REVOKE`
- Процедуры: `EXECUTE BLOCK`, `EXECUTE PROCEDURE`
- Множественные запросы через `;`

### Тестирование защиты

```bash
# Запуск тестов безопасности
pytest tests/test_validators.py -v

# Тесты покрывают:
# ✓ SQL injection попытки
# ✓ Обход через комментарии
# ✓ Множественные запросы
# ✓ Регистронезависимость
# ✓ Все запрещенные операции
```

---

## Rate Limiting

Защита от DoS атак и перегрузки.

### Настройка лимитов

```env
# .env
RATE_LIMIT_PER_MINUTE=60    # 60 запросов/минуту на IP
RATE_LIMIT_PER_HOUR=1000    # 1000 запросов/час на IP
```

### Механизм

- Лимиты применяются по **IP адресу**
- Используется библиотека `slowapi`
- Headers в ответе:
  ```http
  X-RateLimit-Limit: 60
  X-RateLimit-Remaining: 59
  X-RateLimit-Reset: 1634825400
  ```

### Превышение лимита

```json
{
  "error": "Rate limit exceeded: 60 per 1 minute"
}
```

Status: `429 Too Many Requests`

### Whitelist IP (опционально)

Для доверенных IP можно отключить rate limiting:

```python
# app/main.py
from slowapi.util import get_remote_address

def get_remote_address_with_whitelist(request: Request):
    ip = request.client.host
    
    # Whitelist IP адреса (без rate limiting)
    whitelist = ["10.0.0.1", "192.168.1.1"]
    
    if ip in whitelist:
        return None  # Отключить rate limiting
    
    return ip
```

---

## HTTPS

### Production

⚠️ **ОБЯЗАТЕЛЬНО используйте HTTPS в production!**

Railway.com автоматически предоставляет HTTPS:
```
https://your-app.railway.app
```

### SSL Сертификаты

#### Railway/Render/Heroku
✅ SSL из коробки (Let's Encrypt)

#### VPS (ручной deployment)
```bash
# Certbot для Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### HSTS (HTTP Strict Transport Security)

Добавить в Nginx конфиг:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Проверка SSL

```bash
# SSL Labs
https://www.ssllabs.com/ssltest/analyze.html?d=your-domain.com

# Или через curl
curl -I https://your-app.railway.app
```

---

## Environment Variables

### Критичные переменные

**НИКОГДА не коммитить в Git:**
```env
DB_PASSWORD=masterkey
API_TOKENS=secret-token
```

### .gitignore

Убедитесь что `.env` в `.gitignore`:

```gitignore
# Environment variables
.env
.env.*
*.env
!.env.example
```

### Безопасное хранение

**Development:**
- Локальный `.env` файл (в `.gitignore`)
- Password manager для токенов

**Production:**
- Railway/Render/Heroku environment variables
- AWS Secrets Manager
- HashiCorp Vault

### Проверка утечек

```bash
# Сканирование Git истории на секреты
git log -p | grep -i "password\|token\|secret"

# Использовать gitleaks
gitleaks detect --source . --verbose
```

---

## Best Practices

### 1. Минимальные привилегии

```env
# Firebird пользователь с READ-ONLY правами
DB_USER=READONLY_USER  # Не SYSDBA!
```

Создать READ-ONLY пользователя в Firebird:

```sql
CREATE USER readonly_user PASSWORD 'strong-password';
GRANT SELECT ON STORGRP TO readonly_user;
GRANT SELECT ON GOODS TO readonly_user;
-- И т.д. для всех таблиц
```

### 2. Логирование

```python
# app/main.py
logger.info(
    f"→ {request.method} {request.url.path} | "
    f"IP: {client_ip} | "
    f"Token: {token[:10]}..."  # Только первые 10 символов!
)
```

❌ **НИКОГДА не логировать:**
- Полные токены
- Пароли БД
- Чувствительные данные из запросов

### 3. CORS

```env
# Production - конкретные домены
ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com

# Development - все
ALLOWED_ORIGINS=*
```

### 4. Таймауты

```env
DB_CONNECTION_TIMEOUT=10  # Таймаут подключения
DB_QUERY_TIMEOUT=30       # Таймаут запроса
```

Защита от зависших соединений.

### 5. Обновления

Регулярно обновлять зависимости:

```bash
# Проверка устаревших пакетов
pip list --outdated

# Обновление (с тестированием!)
pip install --upgrade fastapi uvicorn fdb
```

### 6. Мониторинг

Настроить алерты на:
- Большое количество 401 (брутфорс токенов)
- Большое количество 429 (DoS попытки)
- Большое количество SQL validation errors (попытки инъекций)
- Недоступность БД

```python
# Webhook для критичных событий
if unauthorized_attempts > 10:
    send_alert_to_slack(
        "⚠️ Возможная атака брутфорса токенов!"
    )
```

---

## Аудит безопасности

### Checklist

- [ ] Сильные токены (64+ символов)
- [ ] Токены не в Git репозитории
- [ ] HTTPS в production
- [ ] Rate limiting включен
- [ ] SQL валидация работает
- [ ] READ-ONLY пользователь БД
- [ ] Логирование включено
- [ ] CORS настроен корректно
- [ ] Зависимости обновлены
- [ ] Тесты безопасности проходят

### Тестирование безопасности

```bash
# Запуск всех тестов
pytest tests/ -v

# Только тесты безопасности
pytest tests/test_validators.py tests/test_auth.py -v
```

### Регулярные проверки

**Еженедельно:**
- Проверка логов на аномалии
- Мониторинг rate limiting

**Ежемесячно:**
- Обновление зависимостей
- Ротация токенов
- Ревью логов

**Ежеквартально:**
- Полный аудит безопасности
- Пентест (опционально)

---

## Инциденты безопасности

### Утечка токена

1. **Немедленно** удалить токен из `API_TOKENS`
2. Сгенерировать новый токен
3. Обновить всех клиентов
4. Проверить логи на несанкционированный доступ
5. Уведомить пользователей если необходимо

### Подозрительная активность

1. Проверить логи:
   ```bash
   # Railway
   railway logs
   
   # VPS
   sudo journalctl -u firebird-db-proxy | grep WARNING
   ```

2. Временно заблокировать IP (если DoS):
   ```nginx
   # Nginx
   deny 1.2.3.4;
   ```

3. Увеличить логирование:
   ```env
   LOG_LEVEL=DEBUG
   ```

### Компрометация БД

1. Немедленно сменить пароль БД
2. Проверить whitelist IP на Firebird сервере
3. Аудит всех операций в БД
4. Восстановление из бэкапа если необходимо

---

## Контакты

При обнаружении уязвимостей:

- **Email:** security@example.com
- **Не публиковать** публично до фикса
- Responsible disclosure период: 90 дней

---

**Версия:** 1.0.0  
**Последнее обновление:** 2025-10-21

