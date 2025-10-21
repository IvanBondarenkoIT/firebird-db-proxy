# 🔄 Firebird Database Proxy API

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Безопасный REST API gateway для доступа к Firebird БД с множества устройств и локаций.

## 🎯 Назначение

Proxy API позволяет выполнять **READ-ONLY** запросы к Firebird БД через HTTP API, обходя ограничения IP whitelist сервера.

### Проблема
- Firebird сервер имеет whitelist IP адресов
- Нужен доступ с множества устройств с разных локаций
- Прямое подключение возможно только с разрешенных IP

### Решение
- API размещается на облачной платформе с **фиксированным IP**
- Один IP добавляется в whitelist Firebird сервера
- Клиенты подключаются к API с любых устройств через Bearer Token

## ✨ Возможности

- ✅ **Безопасность**: Bearer Token аутентификация
- ✅ **Валидация SQL**: Только SELECT и WITH запросы
- ✅ **Connection Pooling**: Эффективное использование соединений
- ✅ **Rate Limiting**: Защита от перегрузки
- ✅ **Мониторинг**: Health check endpoint
- ✅ **Логирование**: Полный аудит всех операций
- ✅ **Auto Documentation**: Swagger UI / ReDoc
- ✅ **CORS**: Поддержка web клиентов
- ✅ **Docker**: Готов к деплою на Railway/Render/Heroku

## 🚀 Быстрый старт

### ⭐ Установка на Windows Server (рекомендуется)

**Если у вас Windows Server с Firebird БД:**

📖 **Полная инструкция:** [WINDOWS_SERVER_INSTALLATION.md](WINDOWS_SERVER_INSTALLATION.md)  
📋 **Быстрый чеклист:** [server-setup/QUICK_START_CHECKLIST.md](server-setup/QUICK_START_CHECKLIST.md)  

**Автоматическая установка:**
```powershell
# От администратора
cd path\to\firebird-db-proxy
.\server-setup\install.ps1
```

**Преимущества:**
- ✅ Бесплатно
- ✅ Максимальная скорость (localhost подключение)
- ✅ Доступен из интернета: `http://85.114.224.45:8000`

---

### Локальная установка (для разработки)

```bash
# Клонировать репозиторий
git clone https://github.com/your-username/firebird-db-proxy.git
cd firebird-db-proxy

# Создать виртуальное окружение
python -m venv venv

# Активировать (Windows)
venv\Scripts\activate

# Активировать (Linux/Mac)
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### Конфигурация

```bash
# Скопировать example файл
cp .env.example .env

# Отредактировать .env
# Установить параметры БД и сгенерировать токены
```

Генерация токенов:

```bash
python scripts/generate_token.py
# Скопировать токен в .env файл
```

### Запуск локально

```bash
# Тест подключения к БД
python scripts/test_connection.py

# Запуск API
python -m app.main

# Или через uvicorn
uvicorn app.main:app --reload
```

API будет доступен на: http://localhost:8000

Документация: http://localhost:8000/docs

## 📖 Использование API

### Аутентификация

Все защищенные endpoint'ы требуют Bearer Token в заголовке:

```
Authorization: Bearer YOUR_TOKEN
```

### Endpoints

#### Health Check (без аутентификации)

```bash
curl http://localhost:8000/api/health
```

#### Выполнение SQL запроса

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT ID, NAME FROM STORGRP",
    "params": []
  }'
```

Ответ:

```json
{
  "success": true,
  "data": [
    {"ID": 1, "NAME": "Магазин 1"},
    {"ID": 2, "NAME": "Магазин 2"}
  ],
  "rows_count": 2,
  "execution_time": 0.234,
  "timestamp": "2025-10-21T12:34:56.789Z"
}
```

#### Список таблиц

```bash
curl http://localhost:8000/api/tables \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Схема таблицы

```bash
curl http://localhost:8000/api/schema/STORGRP \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Примеры использования

#### Python

```python
import requests

API_URL = "http://localhost:8000"
TOKEN = "your-token-here"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Выполнение запроса
response = requests.post(
    f"{API_URL}/api/query",
    json={
        "query": "SELECT * FROM STORGRP WHERE ID = ?",
        "params": [1]
    },
    headers=headers
)

data = response.json()
if data["success"]:
    print(f"Получено строк: {data['rows_count']}")
    for row in data["data"]:
        print(row)
else:
    print(f"Ошибка: {data['error']}")
```

#### JavaScript

```javascript
const API_URL = "http://localhost:8000";
const TOKEN = "your-token-here";

async function queryDatabase(query, params = []) {
  const response = await fetch(`${API_URL}/api/query`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ query, params })
  });
  
  return await response.json();
}

// Использование
const result = await queryDatabase("SELECT * FROM STORGRP");
console.log(result.data);
```

## 🧪 Тестирование

```bash
# Установить dev зависимости
pip install -r requirements.txt

# Запустить все тесты
pytest

# С покрытием кода
pytest --cov=app --cov-report=html

# Только определенный тест
pytest tests/test_validators.py -v
```

## 📊 Мониторинг и логирование

### Логи

Все события логируются в формате:

```
[2025-10-21 12:34:56] [INFO] [module:line] Message
```

Уровни логирования настраиваются через `LOG_LEVEL` в `.env`:
- `DEBUG` - подробная отладка
- `INFO` - стандартные операции
- `WARNING` - предупреждения
- `ERROR` - ошибки

### Health Check

```bash
curl http://localhost:8000/api/health
```

Используйте для мониторинга доступности API и БД.

## 🐳 Docker

### Сборка образа

```bash
docker build -t firebird-db-proxy .
```

### Запуск контейнера

```bash
docker run -p 8000:8000 \
  -e DB_HOST=your-db-host \
  -e DB_PORT=3050 \
  -e DB_NAME=your-database \
  -e DB_USER=SYSDBA \
  -e DB_PASSWORD=masterkey \
  -e API_TOKENS=your-secret-token \
  firebird-db-proxy
```

## 🚢 Deployment на Railway.com

Подробная инструкция: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

### Быстрый старт

1. Создать аккаунт на [Railway.com](https://railway.com)
2. Создать новый проект из GitHub репозитория
3. Railway автоматически обнаружит Dockerfile
4. Добавить environment variables в Railway Dashboard
5. Получить статический IP в Railway Settings
6. Добавить IP в whitelist на Firebird сервере
7. Готово! API доступен по адресу `https://your-app.railway.app`

## 🔒 Безопасность

- ✅ **Только READ-ONLY** операции (SELECT, WITH)
- ✅ **SQL injection защита** через валидацию и параметризованные запросы
- ✅ **Bearer Token** аутентификация
- ✅ **Rate limiting** от перегрузки
- ✅ **HTTPS only** в production
- ✅ **Логирование** всех операций
- ❌ **Никогда не коммитить** `.env` файлы и токены в Git!

Подробнее: [docs/SECURITY.md](docs/SECURITY.md)

## 📚 Документация

### Для установки:
- 🪟 **[Windows Server Installation](WINDOWS_SERVER_INSTALLATION.md)** - Установка на Windows Server (рекомендуется!)
- 📋 **[Quick Start Checklist](server-setup/QUICK_START_CHECKLIST.md)** - Быстрый чеклист для админа
- 🎯 **[Deployment Decision Guide](server-setup/DEPLOYMENT_DECISION.md)** - Помощь в выборе метода
- 🌐 **[Network Explanation](docs/NETWORK_EXPLANATION.md)** - Как работает доступ из интернета

### Для использования:
- 📡 **[API Documentation](docs/API.md)** - Полное описание API endpoints
- 🚀 **[Deployment Guide](docs/DEPLOYMENT.md)** - Инструкции по деплою (облако, VPS)
- 🔒 **[Security Guide](docs/SECURITY.md)** - Best practices безопасности

### Интерактивная документация:
- 📖 [Swagger UI](http://localhost:8000/docs) - Интерактивная документация
- 📚 [ReDoc](http://localhost:8000/redoc) - Альтернативная документация

## 🏗️ Архитектура

```
firebird-db-proxy/
├── app/                        # Исходный код приложения
│   ├── main.py                 # FastAPI приложение
│   ├── config.py               # Конфигурация
│   ├── auth.py                 # Аутентификация
│   ├── database.py             # Connection pool
│   ├── validators.py           # SQL валидация
│   ├── models.py               # Pydantic модели
│   └── routers/                # API endpoints
│       ├── query.py            # POST /api/query
│       ├── health.py           # GET /api/health
│       └── info.py             # GET /api/tables, /api/schema
├── tests/                      # Тесты
├── docs/                       # Документация
├── scripts/                    # Утилиты
├── requirements.txt            # Python зависимости
├── Dockerfile                  # Docker конфигурация
└── README.md                   # Этот файл
```

## 🤝 Contributing

1. Fork репозиторий
2. Создать feature branch (`git checkout -b feature/amazing`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing`)
5. Открыть Pull Request

## 📝 License

MIT License - см. [LICENSE](LICENSE) файл

## 👥 Авторы

- **Senior Developer** - *Initial work*

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - современный async web framework
- [FDB](https://github.com/FirebirdSQL/fdb) - Firebird database driver для Python
- [Pydantic](https://pydantic-docs.helpmanual.io/) - валидация данных
- [Railway](https://railway.com/) - облачная платформа для deployment

---

**Дата создания:** 2025-10-21  
**Версия:** 1.0.0  
**Статус:** Production Ready ✅

