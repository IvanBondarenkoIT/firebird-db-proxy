# 📡 API Documentation

Полная документация API endpoints для Firebird Database Proxy.

## Base URL

```
Production: https://your-app.railway.app
Development: http://localhost:8000
```

## Аутентификация

Все защищенные endpoints требуют Bearer Token в заголовке `Authorization`:

```http
Authorization: Bearer YOUR_SECRET_TOKEN
```

### Получение токена

Токены генерируются администратором:

```bash
python scripts/generate_token.py
```

---

## Endpoints

### 1. Health Check

**GET** `/api/health`

Проверка работоспособности API и подключения к БД.

#### Аутентификация

❌ Не требуется (публичный endpoint)

#### Response

```json
{
  "status": "healthy",
  "database_connected": true,
  "uptime_seconds": 3600,
  "version": "1.0.0",
  "timestamp": "2025-10-21T12:34:56.789Z"
}
```

#### Status Codes

- `200 OK` - Все работает
- `503 Service Unavailable` - БД недоступна

#### Example

```bash
curl http://localhost:8000/api/health
```

---

### 2. Execute Query

**POST** `/api/query`

Выполнение SELECT или WITH запроса к БД.

#### Аутентификация

✅ Требуется Bearer Token

#### Request Body

```json
{
  "query": "SELECT ID, NAME FROM STORGRP WHERE ID = ?",
  "params": [1]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | ✅ | SQL запрос (только SELECT или WITH) |
| params | array | ❌ | Параметры запроса (позиционные) |

#### Response (Success)

```json
{
  "success": true,
  "data": [
    {"ID": 1, "NAME": "Магазин 1"}
  ],
  "rows_count": 1,
  "execution_time": 0.234,
  "timestamp": "2025-10-21T12:34:56.789Z"
}
```

#### Response (Error)

```json
{
  "success": false,
  "error": "SQL validation failed: UPDATE not allowed",
  "execution_time": 0.001,
  "timestamp": "2025-10-21T12:34:56.789Z"
}
```

#### Status Codes

- `200 OK` - Запрос выполнен (проверить `success` в теле ответа)
- `400 Bad Request` - Невалидный запрос
- `401 Unauthorized` - Невалидный токен
- `422 Unprocessable Entity` - Ошибка валидации Pydantic
- `429 Too Many Requests` - Превышен rate limit
- `500 Internal Server Error` - Ошибка сервера

#### Example

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT ID, NAME FROM STORGRP",
    "params": []
  }'
```

#### Параметризованные запросы

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM STORGRP WHERE ID = ? AND NAME LIKE ?",
    "params": [1, "%магазин%"]
  }'
```

#### Разрешенные запросы

✅ SELECT
```sql
SELECT * FROM STORGRP
SELECT ID, NAME FROM STORGRP WHERE ID > 10
SELECT COUNT(*) FROM GOODS
```

✅ WITH (CTE)
```sql
WITH temp AS (
  SELECT ID FROM STORGRP
)
SELECT * FROM temp
```

✅ JOIN
```sql
SELECT a.ID, b.NAME 
FROM STORGRP a 
JOIN GOODS b ON a.ID = b.STORE_ID
```

#### Запрещенные запросы

❌ UPDATE, INSERT, DELETE
```sql
UPDATE STORGRP SET NAME = 'Test'
INSERT INTO STORGRP VALUES (...)
DELETE FROM STORGRP WHERE ID = 1
```

❌ DDL операции
```sql
DROP TABLE STORGRP
ALTER TABLE STORGRP ADD COLUMN test VARCHAR(100)
CREATE TABLE test (...)
TRUNCATE TABLE STORGRP
```

❌ Множественные запросы
```sql
SELECT * FROM STORGRP; SELECT * FROM GOODS;
```

---

### 3. Get Tables

**GET** `/api/tables`

Получение списка всех пользовательских таблиц в БД.

#### Аутентификация

✅ Требуется Bearer Token

#### Response

```json
{
  "success": true,
  "tables": [
    "STORGRP",
    "STORZAKAZDT",
    "STORZDTGDS",
    "GOODS"
  ],
  "count": 4,
  "timestamp": "2025-10-21T12:34:56.789Z"
}
```

#### Status Codes

- `200 OK` - Успешно
- `401 Unauthorized` - Невалидный токен
- `500 Internal Server Error` - Ошибка БД

#### Example

```bash
curl http://localhost:8000/api/tables \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Get Table Schema

**GET** `/api/schema/{table_name}`

Получение схемы таблицы (список колонок и их типы).

#### Аутентификация

✅ Требуется Bearer Token

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| table_name | string | Имя таблицы (регистр не важен) |

#### Response

```json
{
  "success": true,
  "table": "STORGRP",
  "columns": [
    {
      "name": "ID",
      "type": "INTEGER",
      "nullable": false
    },
    {
      "name": "NAME",
      "type": "VARCHAR",
      "nullable": true
    }
  ],
  "timestamp": "2025-10-21T12:34:56.789Z"
}
```

#### Status Codes

- `200 OK` - Успешно
- `401 Unauthorized` - Невалидный токен
- `404 Not Found` - Таблица не найдена
- `500 Internal Server Error` - Ошибка БД

#### Example

```bash
curl http://localhost:8000/api/schema/STORGRP \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 5. Root Endpoint

**GET** `/`

Информация об API.

#### Аутентификация

❌ Не требуется

#### Response

```json
{
  "message": "Firebird DB Proxy API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/api/health"
}
```

#### Example

```bash
curl http://localhost:8000/
```

---

## Rate Limiting

API защищен от перегрузки через rate limiting.

### Лимиты (по умолчанию)

- **60 запросов/минуту** на IP адрес
- **1000 запросов/час** на IP адрес

### Response Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1634825400
```

### Превышение лимита

Status: `429 Too Many Requests`

```json
{
  "error": "Rate limit exceeded"
}
```

---

## Error Handling

### Стандартный формат ошибок

```json
{
  "success": false,
  "error": "Описание ошибки",
  "timestamp": "2025-10-21T12:34:56.789Z"
}
```

### Типы ошибок

#### 400 Bad Request
- Невалидный SQL запрос
- Запрещенная SQL операция

#### 401 Unauthorized
- Отсутствует токен
- Невалидный токен

#### 404 Not Found
- Таблица не найдена

#### 422 Unprocessable Entity
- Невалидная структура JSON
- Отсутствуют обязательные поля

#### 429 Too Many Requests
- Превышен rate limit

#### 500 Internal Server Error
- Ошибка подключения к БД
- Ошибка выполнения запроса
- Внутренняя ошибка сервера

#### 503 Service Unavailable
- БД недоступна (health check)

---

## Interactive Documentation

### Swagger UI

Интерактивная документация с возможностью тестирования API:

```
http://localhost:8000/docs
```

### ReDoc

Альтернативная документация:

```
http://localhost:8000/redoc
```

---

## Code Examples

### Python с requests

```python
import requests

API_URL = "http://localhost:8000"
TOKEN = "your-token-here"

class FirebirdProxyClient:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def query(self, sql, params=None):
        response = requests.post(
            f"{self.api_url}/api/query",
            json={"query": sql, "params": params or []},
            headers=self.headers
        )
        return response.json()
    
    def get_tables(self):
        response = requests.get(
            f"{self.api_url}/api/tables",
            headers=self.headers
        )
        return response.json()
    
    def get_schema(self, table_name):
        response = requests.get(
            f"{self.api_url}/api/schema/{table_name}",
            headers=self.headers
        )
        return response.json()

# Использование
client = FirebirdProxyClient(API_URL, TOKEN)

# Запрос
result = client.query("SELECT * FROM STORGRP WHERE ID = ?", [1])
if result["success"]:
    print(result["data"])

# Список таблиц
tables = client.get_tables()
print(tables["tables"])

# Схема таблицы
schema = client.get_schema("STORGRP")
for col in schema["columns"]:
    print(f"{col['name']}: {col['type']}")
```

### JavaScript (fetch)

```javascript
class FirebirdProxyClient {
  constructor(apiUrl, token) {
    this.apiUrl = apiUrl;
    this.headers = {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    };
  }
  
  async query(sql, params = []) {
    const response = await fetch(`${this.apiUrl}/api/query`, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify({ query: sql, params })
    });
    return await response.json();
  }
  
  async getTables() {
    const response = await fetch(`${this.apiUrl}/api/tables`, {
      headers: this.headers
    });
    return await response.json();
  }
  
  async getSchema(tableName) {
    const response = await fetch(
      `${this.apiUrl}/api/schema/${tableName}`,
      { headers: this.headers }
    );
    return await response.json();
  }
}

// Использование
const client = new FirebirdProxyClient(
  "http://localhost:8000",
  "your-token-here"
);

// Запрос
const result = await client.query("SELECT * FROM STORGRP");
if (result.success) {
  console.log(result.data);
}
```

### cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Query
curl -X POST http://localhost:8000/api/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM STORGRP"}'

# Tables
curl http://localhost:8000/api/tables \
  -H "Authorization: Bearer YOUR_TOKEN"

# Schema
curl http://localhost:8000/api/schema/STORGRP \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

**Версия:** 1.0.0  
**Последнее обновление:** 2025-10-21

