# 🪟 УСТАНОВКА НА WINDOWS SERVER
# Пошаговая инструкция для системного администратора

**Проект:** Firebird Database Proxy API  
**Дата:** 21 октября 2025  
**Версия:** 1.0  

---

## 📋 ОГЛАВЛЕНИЕ

1. [Требования к серверу](#требования)
2. [Предварительная подготовка](#подготовка)
3. [Установка Python](#установка-python)
4. [Установка приложения](#установка-приложения)
5. [Создание READ-ONLY пользователя БД](#создание-пользователя)
6. [Настройка и тестирование](#настройка)
7. [Установка как Windows Service](#windows-service)
8. [Настройка Windows Firewall](#firewall)
9. [Проверка работы](#проверка)
10. [Мониторинг и обслуживание](#обслуживание)

---

<a name="требования"></a>
## 1️⃣ ТРЕБОВАНИЯ К СЕРВЕРУ

### Минимальные требования:

- ✅ **ОС:** Windows Server 2016+ (или Windows 10/11)
- ✅ **RAM:** 1 GB свободной памяти
- ✅ **HDD:** 500 MB свободного места
- ✅ **Интернет:** Доступ для скачивания пакетов
- ✅ **Права:** Администратор сервера
- ✅ **Firebird:** Уже установлен и работает

### Что уже должно быть:

```
✅ Firebird сервер работает
✅ БД: DK_GEORGIA доступна
✅ Порт 3055 слушается
✅ Сервер имеет белый IP: 85.114.224.45
```

### Что будем устанавливать:

```
→ Python 3.12 (~100 MB)
→ Git для Windows (~50 MB)
→ Наше приложение (~50 MB)
→ NSSM для Windows Service (~1 MB)
```

**ИТОГО:** ~200 MB места на диске

---

<a name="подготовка"></a>
## 2️⃣ ПРЕДВАРИТЕЛЬНАЯ ПОДГОТОВКА

### Информация которая понадобится:

**О сервере:**
```
IP адрес сервера: 85.114.224.45
Имя сервера: _________________
Версия Windows: _________________
```

**О Firebird:**
```
Порт: 3055
База данных: DK_GEORGIA
Пользователь SYSDBA: SYSDBA
Пароль SYSDBA: masterkey (будет изменен!)
```

**Для API:**
```
Порт для API: 8000 (или другой свободный)
```

### Проверка перед началом:

```powershell
# 1. Открыть PowerShell от администратора
# Правой кнопкой на PowerShell → "Запустить от имени администратора"

# 2. Проверить что Firebird работает
Test-NetConnection -ComputerName localhost -Port 3055

# Должно показать: TcpTestSucceeded : True

# 3. Проверить свободные порты
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

# Если пусто - порт свободен ✅
# Если что-то показало - выбрать другой порт
```

---

<a name="установка-python"></a>
## 3️⃣ УСТАНОВКА PYTHON

### Вариант A: Автоматическая установка (рекомендуется)

```powershell
# 1. Скачать Python 3.12
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe" `
  -OutFile "$env:TEMP\python-installer.exe"

# 2. Установить (без GUI)
Start-Process -Wait -FilePath "$env:TEMP\python-installer.exe" `
  -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0"

# 3. Проверить установку
python --version
# Должно показать: Python 3.12.7

# 4. Проверить pip
pip --version
# Должно показать: pip 24.x.x
```

### Вариант B: Ручная установка

1. Открыть https://www.python.org/downloads/
2. Скачать **Python 3.12.7** (Windows installer 64-bit)
3. Запустить установщик
4. **ВАЖНО!** Отметить галочку: ☑ **"Add Python to PATH"**
5. Выбрать **"Install Now"**
6. Дождаться завершения
7. Проверить: открыть PowerShell и ввести `python --version`

### ⚠️ Важно:

- НЕ устанавливать Python 3.13 (несовместим с библиотекой fdb)
- Использовать **Python 3.12** или **Python 3.11**

---

<a name="установка-приложения"></a>
## 4️⃣ УСТАНОВКА ПРИЛОЖЕНИЯ

### Шаг 1: Установка Git (если нет)

```powershell
# Скачать Git
Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/Git-2.47.1-64-bit.exe" `
  -OutFile "$env:TEMP\git-installer.exe"

# Установить
Start-Process -Wait -FilePath "$env:TEMP\git-installer.exe" `
  -ArgumentList "/VERYSILENT"

# Проверить
git --version
```

### Шаг 2: Создание рабочей директории

```powershell
# Создать папку для приложения
# Рекомендуемое место: C:\FirebirdAPI или D:\FirebirdAPI
New-Item -ItemType Directory -Path "C:\FirebirdAPI" -Force

# Перейти в папку
cd C:\FirebirdAPI
```

### Шаг 3: Скачивание кода

```powershell
# Клонировать репозиторий
git clone https://github.com/IvanBondarenkoIT/firebird-db-proxy.git

# Перейти в папку проекта
cd firebird-db-proxy

# Проверить что все файлы на месте
dir
```

**Должны увидеть:**
```
app/
docs/
tests/
scripts/
requirements.txt
Dockerfile
README.md
...
```

### Шаг 4: Создание виртуального окружения

```powershell
# Создать виртуальное окружение Python
python -m venv venv

# Активировать
.\venv\Scripts\activate

# Проверить активацию (должно показать (venv) в начале строки)
# (venv) PS C:\FirebirdAPI\firebird-db-proxy>
```

### Шаг 5: Установка зависимостей

```powershell
# Обновить pip
python -m pip install --upgrade pip

# Установить зависимости
pip install -r requirements.txt

# Ожидайте 2-3 минуты...
# Должно показать: Successfully installed fastapi ... (список пакетов)
```

### Шаг 6: Патч для Python 3.13 (если установлена 3.13)

```powershell
# ТОЛЬКО если у вас Python 3.13!
# Проверить версию:
python --version

# Если показывает 3.13.x, применить патч:
$patchFile = ".\venv\Lib\site-packages\fdb\gstat.py"
(Get-Content $patchFile) -replace 'from locale import LC_ALL, LC_CTYPE, getlocale, setlocale, resetlocale', @'
from locale import LC_ALL, LC_CTYPE, getlocale, setlocale
try:
    from locale import resetlocale
except ImportError:
    def resetlocale(category=LC_ALL):
        return setlocale(category, '')
'@ | Set-Content $patchFile
```

---

<a name="создание-пользователя"></a>
## 5️⃣ СОЗДАНИЕ READ-ONLY ПОЛЬЗОВАТЕЛЯ В FIREBIRD

### ⚠️ КРИТИЧЕСКИ ВАЖНО ДЛЯ БЕЗОПАСНОСТИ!

**Зачем:** Даже если токен API украдут, никто не сможет изменить или удалить данные!

### Шаг 1: Подключиться к Firebird

**Вариант A: Через isql (консоль Firebird)**

```cmd
# Найти isql.exe (обычно в C:\Program Files\Firebird\Firebird_3_0\)
cd "C:\Program Files\Firebird\Firebird_3_0"

# Подключиться к БД
isql.exe -user SYSDBA -password masterkey localhost/3055:DK_GEORGIA
```

**Вариант B: Через FlameRobin или другой GUI клиент**

Просто подключитесь как SYSDBA к базе DK_GEORGIA.

### Шаг 2: Создать пользователя

Выполнить SQL из файла `server-setup/create_readonly_user.sql`:

```sql
-- Создать READ-ONLY пользователя для API
CREATE USER api_readonly PASSWORD 'Api#ReadOnly#2025!Secure';

-- Дать права SELECT на все нужные таблицы
-- (список основных таблиц для анализа продаж кофе)

GRANT SELECT ON STORGRP TO api_readonly;
GRANT SELECT ON STORZAKAZDT TO api_readonly;
GRANT SELECT ON STORZDTGDS TO api_readonly;
GRANT SELECT ON GOODS TO api_readonly;

-- Дать права на системные таблицы (для получения списка таблиц и схем)
GRANT SELECT ON RDB$RELATIONS TO api_readonly;
GRANT SELECT ON RDB$RELATION_FIELDS TO api_readonly;
GRANT SELECT ON RDB$FIELDS TO api_readonly;
GRANT SELECT ON RDB$TYPES TO api_readonly;
GRANT SELECT ON RDB$DATABASE TO api_readonly;

-- Подтвердить изменения
COMMIT;

-- Проверить пользователя
SELECT * FROM RDB$USERS WHERE RDB$USER_NAME = 'API_READONLY';
```

**Важно запомнить:**
```
Пользователь: api_readonly
Пароль: Api#ReadOnly#2025!Secure
```

### Шаг 3: Проверить права

```sql
-- Проверка что пользователь может только читать
-- Подключиться заново как api_readonly:
CONNECT localhost/3055:DK_GEORGIA USER api_readonly PASSWORD 'Api#ReadOnly#2025!Secure';

-- Попробовать SELECT - должно работать
SELECT COUNT(*) FROM STORGRP;

-- Попробовать UPDATE - должно быть отказано
UPDATE STORGRP SET NAME = 'Test';
-- Должна быть ошибка: no permission for UPDATE access to TABLE STORGRP

-- Если получили ошибку на UPDATE - всё правильно! ✅
```

---

<a name="настройка"></a>
## 6️⃣ НАСТРОЙКА И ТЕСТИРОВАНИЕ

### Шаг 1: Создать .env файл

```powershell
# Скопировать пример
cd C:\FirebirdAPI\firebird-db-proxy
copy .env.example .env

# Открыть для редактирования
notepad .env
```

### Шаг 2: Заполнить .env

**Критически важные настройки для сервера:**

```env
# ==================== DATABASE ====================
# ВАЖНО: Используем localhost (127.0.0.1) для подключения к БД!
DB_HOST=127.0.0.1
DB_PORT=3055
DB_NAME=DK_GEORGIA
DB_USER=api_readonly
DB_PASSWORD=Api#ReadOnly#2025!Secure

# Connection settings
DB_MAX_CONNECTIONS=10
DB_CONNECTION_TIMEOUT=10
DB_QUERY_TIMEOUT=30

# ==================== CACHE ====================
# Кеширование на 10 минут (для production)
CACHE_TTL=600

# ==================== SECURITY ====================
# ВАЖНО: Сгенерировать сильные токены!
# Используйте: python scripts/generate_token.py --count 2
API_TOKENS=<СГЕНЕРИРОВАТЬ_ТОКЕНЫ_ЗДЕСЬ>

# CORS - разрешить все источники (или указать конкретные домены)
ALLOWED_ORIGINS=*

# ==================== LOGGING ====================
LOG_LEVEL=INFO

# ==================== APPLICATION ====================
APP_NAME=Firebird DB Proxy
APP_VERSION=1.0.0
APP_ENV=production

# Порт на котором слушает API
PORT=8000
```

**⚠️ ВАЖНО:**
- `DB_HOST=127.0.0.1` - **НЕ** `85.114.224.45`! Подключаемся локально!
- `DB_USER=api_readonly` - **НЕ** SYSDBA! Только чтение!
- `APP_ENV=production` - рабочий режим

### Шаг 3: Сгенерировать токены

```powershell
# Активировать venv если не активировано
.\venv\Scripts\activate

# Сгенерировать 2 токена
python scripts/generate_token.py --count 2

# Скопировать результат в .env
# Открыть .env
notepad .env

# Вставить токены в строку API_TOKENS
```

**Пример:**
```env
API_TOKENS=a1b2c3d4e5f6...64символа,x7y8z9w1v2u3...64символа
```

**Сохранить токены в безопасном месте!** Они понадобятся для клиентов.

### Шаг 4: Тест подключения к БД

```powershell
# ВАЖНО: Активировать venv если не активировано!
.\venv\Scripts\activate

# Проверить что API может подключиться к Firebird
python scripts/test_connection.py
```

**⚠️ Если видите ошибку `ModuleNotFoundError: No module named 'pydantic_settings'`:**
- Убедитесь что venv активирован (должно быть `(venv)` в начале строки)
- Если не активирован, выполните: `.\venv\Scripts\activate`
- Если зависимости не установлены, выполните: `pip install -r requirements.txt`

**Ожидаемый результат:**
```
============================================================
ТЕСТ ПОДКЛЮЧЕНИЯ К FIREBIRD БД
============================================================

Хост:     127.0.0.1
Порт:     3055
База:     DK_GEORGIA
DSN:      127.0.0.1/3055:DK_GEORGIA
User:     api_readonly
Password: **********

✓ Database инициализирована успешно
✓ Подключение успешно!
✓ Найдено таблиц: 362

============================================================
ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! ✓
============================================================
```

**Если тест не прошел:**
- Проверьте что Firebird запущен
- Проверьте параметры в .env
- Проверьте что пользователь api_readonly создан
- Проверьте пароль

### Шаг 5: Запуск API (первый раз)

```powershell
# Запустить API вручную для проверки
python -m app.main
```

**Ожидаемый вывод:**
```
INFO:     Will watch for changes in these directories: ['C:\\FirebirdAPI\\firebird-db-proxy']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
[2025-10-21 15:00:00] [INFO] Starting Firebird DB Proxy v1.0.0
[2025-10-21 15:00:00] [INFO] Database: 127.0.0.1/3055:DK_GEORGIA
[2025-10-21 15:00:00] [INFO] Cache TTL: 600s
[2025-10-21 15:00:01] [INFO] Database connection test: SUCCESS ✓
[2025-10-21 15:00:01] [INFO] API server starting on port 8000
INFO:     Application startup complete.
```

**Если увидели "SUCCESS ✓" - отлично! API работает!** ✅

**НЕ закрывайте это окно!** Оставьте API запущенным для тестов.

### Шаг 6: Тестирование API (в другом окне PowerShell)

```powershell
# Открыть НОВОЕ окно PowerShell

# Тест 1: Health check (без токена)
Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing

# Должно показать: StatusCode : 200

# Тест 2: Query с токеном
$token = "ВАШ_ТОКЕН_ЗДЕСЬ"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
$body = @{
    query = "SELECT COUNT(*) AS CNT FROM STORGRP"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/query" `
  -Method POST `
  -Headers $headers `
  -Body $body `
  -UseBasicParsing

# Должно вернуть данные!
```

**Если все работает - переходим к следующему шагу!**

Вернитесь в первое окно PowerShell и нажмите **CTRL+C** чтобы остановить API.

---

<a name="windows-service"></a>
## 7️⃣ УСТАНОВКА КАК WINDOWS SERVICE

### Зачем:
- API запускается **автоматически** при старте сервера
- Работает **в фоне** постоянно
- Перезапускается при сбоях

### Шаг 1: Скачать NSSM

```powershell
# Скачать NSSM (Non-Sucking Service Manager)
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" `
  -OutFile "$env:TEMP\nssm.zip"

# Распаковать
Expand-Archive -Path "$env:TEMP\nssm.zip" -DestinationPath "$env:TEMP\nssm" -Force

# Скопировать нужную версию в папку проекта
# ВАЖНО: Замените путь на ваш реальный путь!
$projectPath = "G:\FirebirdAPI\firebird-db-proxy"  # ИЗМЕНИТЕ НА ВАШ ПУТЬ!
copy "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" "$projectPath\nssm.exe"

# Проверить (используйте путь к вашему проекту)
cd $projectPath
.\nssm.exe version
```

### Шаг 2: Создать Windows Service

```powershell
# ВАЖНО: Замените путь на ваш реальный путь!
$projectPath = "G:\FirebirdAPI\firebird-db-proxy"  # ИЗМЕНИТЕ НА ВАШ ПУТЬ!

# Перейти в папку приложения
cd $projectPath

# Установить сервис
.\nssm.exe install FirebirdAPI `
  "$projectPath\venv\Scripts\python.exe" `
  "-m app.main"

# Настроить параметры
.\nssm.exe set FirebirdAPI AppDirectory $projectPath
.\nssm.exe set FirebirdAPI DisplayName "Firebird Database Proxy API"
.\nssm.exe set FirebirdAPI Description "REST API для доступа к Firebird БД"
.\nssm.exe set FirebirdAPI Start SERVICE_AUTO_START

# Настроить логирование
$logsPath = "$projectPath\logs"
.\nssm.exe set FirebirdAPI AppStdout "$logsPath\api-output.log"
.\nssm.exe set FirebirdAPI AppStderr "$logsPath\api-error.log"

# ВАЖНО: Установить переменные окружения для Python
.\nssm.exe set FirebirdAPI AppEnvironmentExtra "PYTHONPATH=$projectPath" "PYTHONUNBUFFERED=1"

# ВАЖНО: Настроить запуск от имени LocalSystem (системный аккаунт)
.\nssm.exe set FirebirdAPI ObjectName LocalSystem

# Создать папку для логов
New-Item -ItemType Directory -Path $logsPath -Force

# ВАЖНО: Установить права на папку для системного аккаунта
icacls $projectPath /grant "SYSTEM:(OI)(CI)F" /T | Out-Null
```

### Шаг 3: Диагностика перед запуском

```powershell
# Перейти в папку проекта
$projectPath = "G:\FirebirdAPI\firebird-db-proxy"  # ИЗМЕНИТЕ НА ВАШ ПУТЬ!
cd $projectPath

# Проверить что все файлы на месте
Test-Path "$projectPath\venv\Scripts\python.exe"
Test-Path "$projectPath\.env"
Test-Path "$projectPath\app\main.py"

# Проверить настройки сервиса
.\nssm.exe get FirebirdAPI Application
.\nssm.exe get FirebirdAPI AppDirectory
.\nssm.exe get FirebirdAPI AppParameters

# Проверить что Python может запустить приложение вручную
.\venv\Scripts\python.exe -m app.main
# Нажмите CTRL+C после проверки что оно запустилось
```

### Шаг 4: Запустить сервис

```powershell
# Запустить
Start-Service FirebirdAPI

# Подождать 3 секунды
Start-Sleep -Seconds 3

# Проверить статус
Get-Service FirebirdAPI

# Проверить логи ошибок (если сервис не запустился)
Get-Content "$projectPath\logs\api-error.log" -Tail 50 -ErrorAction SilentlyContinue
Get-Content "$projectPath\logs\api-output.log" -Tail 50 -ErrorAction SilentlyContinue

# Если сервис не запустился, проверить детали
.\nssm.exe status FirebirdAPI
```

**Если статус Running - переходим к проверке API!** ✅

**Если сервис не запустился:**
- Проверьте логи ошибок выше
- Убедитесь что .env файл существует и заполнен
- Убедитесь что Python может запустить приложение вручную (Шаг 3)

### Шаг 5: Проверить что API работает

```powershell
# Подождать еще немного
Start-Sleep -Seconds 5

# Проверить health endpoint
Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing

# Должно показать: StatusCode : 200
```

**Если health check работает - SUCCESS!** ✅

### Шаг 6: Настроить автоматический перезапуск при сбоях

```powershell
# Перезапускать сервис если упадет
$projectPath = "G:\FirebirdAPI\firebird-db-proxy"  # ИЗМЕНИТЕ НА ВАШ ПУТЬ!
cd $projectPath
.\nssm.exe set FirebirdAPI AppExit Default Restart
.\nssm.exe set FirebirdAPI AppRestartDelay 5000

# Перезапустить сервис для применения настроек
Restart-Service FirebirdAPI
```

---

<a name="firewall"></a>
## 8️⃣ НАСТРОЙКА WINDOWS FIREWALL

### Цель: Открыть порт 8000 для доступа из интернета

### Вариант A: Через PowerShell (рекомендуется)

```powershell
# Создать правило для входящих подключений
New-NetFirewallRule -DisplayName "Firebird Database Proxy API" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 8000 `
  -Action Allow `
  -Profile Any `
  -Enabled True

# Проверить правило
Get-NetFirewallRule -DisplayName "Firebird Database Proxy API"
```

### Вариант B: Через GUI

1. Открыть **Windows Defender Firewall**
2. **Advanced Settings** (Дополнительные параметры)
3. **Inbound Rules** → **New Rule**
4. **Port** → Next
5. **TCP** → Specific local ports: **8000** → Next
6. **Allow the connection** → Next
7. **Domain, Private, Public** (все) → Next
8. Name: **Firebird Database Proxy API** → Finish

### Проверка:

```powershell
# Проверить с ДРУГОГО компьютера в сети
# (например, с вашего рабочего компьютера)

Invoke-WebRequest -Uri "http://85.114.224.45:8000/api/health" -UseBasicParsing

# Должно показать: StatusCode : 200
```

**Если работает - порт открыт правильно!** ✅

---

<a name="проверка"></a>
## 9️⃣ ФИНАЛЬНАЯ ПРОВЕРКА

### Чеклист проверки:

```powershell
# 1. Сервис запущен
Get-Service FirebirdAPI
# Status: Running ✅

# 2. API отвечает локально
Invoke-WebRequest -Uri "http://localhost:8000/api/health"
# StatusCode: 200 ✅

# 3. API отвечает по внешнему IP
Invoke-WebRequest -Uri "http://85.114.224.45:8000/api/health"
# StatusCode: 200 ✅

# 4. Порт открыт в firewall
Get-NetFirewallRule -DisplayName "Firebird Database Proxy API"
# Enabled: True ✅

# 5. Проверка логов
Get-Content "C:\FirebirdAPI\logs\api-output.log" -Tail 20
# Должны видеть логи запуска ✅
```

### Тест с токеном:

```powershell
$token = "ВАШ_ТОКЕН_ЗДЕСЬ"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Тест 1: Получить список таблиц
$response = Invoke-WebRequest -Uri "http://85.114.224.45:8000/api/tables" `
  -Headers $headers `
  -UseBasicParsing

$response.Content | ConvertFrom-Json
# Должен показать список таблиц ✅

# Тест 2: Выполнить запрос
$body = @{
    query = "SELECT ID, NAME FROM STORGRP WHERE ID < 10"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://85.114.224.45:8000/api/query" `
  -Method POST `
  -Headers $headers `
  -Body $body `
  -UseBasicParsing

$response.Content | ConvertFrom-Json
# Должен вернуть данные ✅
```

### Открыть документацию в браузере:

```
http://85.114.224.45:8000/docs
```

Должна открыться **Swagger UI** с интерактивной документацией API!

---

<a name="обслуживание"></a>
## 🔟 МОНИТОРИНГ И ОБСЛУЖИВАНИЕ

### Просмотр логов:

```powershell
# Последние 50 строк
Get-Content "C:\FirebirdAPI\logs\api-output.log" -Tail 50

# Логи в реальном времени
Get-Content "C:\FirebirdAPI\logs\api-output.log" -Wait

# Ошибки
Get-Content "C:\FirebirdAPI\logs\api-error.log" -Tail 50
```

### Управление сервисом:

```powershell
# Остановить
Stop-Service FirebirdAPI

# Запустить
Start-Service FirebirdAPI

# Перезапустить
Restart-Service FirebirdAPI

# Статус
Get-Service FirebirdAPI
```

### Обновление приложения:

```powershell
# 1. Остановить сервис
Stop-Service FirebirdAPI

# 2. Перейти в папку
cd C:\FirebirdAPI\firebird-db-proxy

# 3. Скачать обновления
git pull origin main

# 4. Активировать venv
.\venv\Scripts\activate

# 5. Обновить зависимости (если изменились)
pip install -r requirements.txt --upgrade

# 6. Запустить сервис
Start-Service FirebirdAPI

# 7. Проверить
Invoke-WebRequest -Uri "http://localhost:8000/api/health"
```

### Мониторинг доступности:

**Создать Task Scheduler задачу для проверки:**

```powershell
# Файл: C:\FirebirdAPI\check_health.ps1
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -ErrorAction SilentlyContinue

if ($response.StatusCode -ne 200) {
    # Отправить уведомление или перезапустить
    Restart-Service FirebirdAPI
    
    # Можно добавить отправку email или сообщения
}
```

**Запускать каждые 5 минут через Task Scheduler.**

---

## 📊 МОНИТОРИНГ БЕЗОПАСНОСТИ

### Проверка подозрительной активности:

```powershell
# Найти попытки с неправильными токенами
Get-Content "C:\FirebirdAPI\logs\api-output.log" | Select-String "Invalid token"

# Найти заблокированные SQL запросы
Get-Content "C:\FirebirdAPI\logs\api-output.log" | Select-String "Forbidden"

# Статистика по IP адресам
Get-Content "C:\FirebirdAPI\logs\api-output.log" | Select-String "IP:" | Group-Object
```

### Ротация токенов (рекомендуется раз в месяц):

```powershell
# 1. Сгенерировать новые токены
cd C:\FirebirdAPI\firebird-db-proxy
.\venv\Scripts\activate
python scripts/generate_token.py --count 2

# 2. Добавить новые токены к существующим
notepad .env
# Добавить новые токены через запятую к старым

# 3. Перезапустить сервис
Restart-Service FirebirdAPI

# 4. Обновить клиенты на новые токены (постепенно)

# 5. Удалить старые токены из .env
# 6. Перезапустить снова
```

---

## 🚨 РЕШЕНИЕ ПРОБЛЕМ

### Проблема: Сервис не запускается

```powershell
# Проверить логи ошибок
Get-Content "C:\FirebirdAPI\logs\api-error.log" -Tail 50

# Проверить статус
C:\FirebirdAPI\nssm.exe status FirebirdAPI

# Попробовать запустить вручную для отладки
cd C:\FirebirdAPI\firebird-db-proxy
.\venv\Scripts\activate
python -m app.main
# Смотрим какая ошибка
```

### Проблема: API недоступен из интернета

```powershell
# 1. Проверить firewall
Get-NetFirewallRule -DisplayName "Firebird Database Proxy API"

# 2. Проверить что API слушает на правильном порте
netstat -an | findstr :8000
# Должно показать: 0.0.0.0:8000  LISTENING

# 3. Проверить с самого сервера
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health"
Invoke-WebRequest -Uri "http://85.114.224.45:8000/api/health"

# 4. Проверить с другого компьютера
```

### Проблема: База данных не подключается

```powershell
# Проверить параметры в .env
Get-Content .env | Select-String "DB_"

# Убедиться что используется 127.0.0.1 а не внешний IP!
# DB_HOST=127.0.0.1 ✅
# DB_HOST=85.114.224.45 ❌

# Проверить что Firebird работает
Test-NetConnection -ComputerName localhost -Port 3055

# Тест подключения
python scripts/test_connection.py
```

### Проблема: Ошибка 401 Unauthorized

```powershell
# Проверить токен
# 1. Токен в запросе должен точно совпадать с токеном в .env
# 2. Токен не должен содержать пробелов
# 3. Формат: Authorization: Bearer ТОКЕН_БЕЗ_ПРОБЕЛОВ

# Проверить токены в .env
Get-Content .env | Select-String "API_TOKENS"
```

---

## 📋 ФИНАЛЬНЫЙ ЧЕКЛИСТ

После установки проверьте:

- [ ] Python 3.12 установлен
- [ ] Git установлен
- [ ] Код скачан в C:\FirebirdAPI\firebird-db-proxy
- [ ] Зависимости установлены (pip install)
- [ ] READ-ONLY пользователь создан в Firebird
- [ ] .env файл настроен правильно (DB_HOST=127.0.0.1)
- [ ] Токены сгенерированы и сохранены
- [ ] Тест подключения пройден
- [ ] API запускается вручную
- [ ] NSSM установлен
- [ ] Windows Service создан
- [ ] Сервис запущен (Status: Running)
- [ ] Firewall rule создан (порт 8000)
- [ ] Health check работает локально
- [ ] Health check работает по внешнему IP
- [ ] Query с токеном работает
- [ ] Swagger UI доступен

### Команда для быстрой проверки всего:

```powershell
# Запустить этот скрипт для полной проверки
C:\FirebirdAPI\firebird-db-proxy\server-setup\verify_installation.ps1
```

---

## 🎯 ИТОГОВЫЕ НАСТРОЙКИ

**После установки у вас будет:**

```
✅ API работает 24/7
✅ Автозапуск при старте сервера
✅ Доступен из любой точки мира: http://85.114.224.45:8000
✅ Защищен Bearer Token
✅ Только READ-ONLY доступ к БД
✅ Логирование всех операций
✅ Кеширование запросов (10 минут)
```

**Клиенты подключаются:**
```
http://85.114.224.45:8000/api/query
+ Bearer Token
= Работает из любого города! ✅
```

---

## 📞 КОНТАКТЫ ДЛЯ ПОДДЕРЖКИ

**Разработчик:** Иван Бондаренко  
**Email:** ivan.bondarenko.it@gmail.com  
**GitHub:** https://github.com/IvanBondarenkoIT/firebird-db-proxy

**При проблемах:**
1. Проверить логи: `C:\FirebirdAPI\logs\`
2. Проверить чеклист выше
3. Связаться с разработчиком

---

**Время установки:** 1-2 часа  
**Сложность:** Средняя (требуются права администратора)  
**Результат:** API доступен из любой точки мира через интернет! 🌍

