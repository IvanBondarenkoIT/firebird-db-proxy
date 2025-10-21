# ✅ БЫСТРЫЙ ЧЕКЛИСТ УСТАНОВКИ
# Для системного администратора Windows Server

**Время:** 1-2 часа  
**Требования:** Права администратора на Windows Server  

---

## ПЕРЕД НАЧАЛОМ

- [ ] Права администратора на Windows Server
- [ ] Firebird работает на localhost:3055
- [ ] База DK_GEORGIA доступна
- [ ] Пароль SYSDBA известен

---

## ШАГ 1: УСТАНОВКА PYTHON (15 мин)

```powershell
# Проверить Python
python --version

# Если нет - установить Python 3.12:
# https://www.python.org/downloads/release/python-3127/
# ☑ Отметить "Add Python to PATH"
```

- [ ] Python 3.12 установлен
- [ ] `python --version` показывает версию

---

## ШАГ 2: СКАЧАТЬ КОД (5 мин)

```powershell
# Создать папку
New-Item -ItemType Directory -Path "C:\FirebirdAPI" -Force
cd C:\FirebirdAPI

# Клонировать репозиторий
git clone https://github.com/IvanBondarenkoIT/firebird-db-proxy.git
cd firebird-db-proxy

# Создать venv и установить зависимости
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

- [ ] Код скачан в C:\FirebirdAPI\firebird-db-proxy
- [ ] Зависимости установлены

---

## ШАГ 3: СОЗДАТЬ READ-ONLY ПОЛЬЗОВАТЕЛЯ (10 мин)

```powershell
# Подключиться к Firebird
isql -user SYSDBA -password masterkey localhost/3055:DK_GEORGIA

# В консоли isql выполнить:
INPUT 'C:\FirebirdAPI\firebird-db-proxy\server-setup\create_readonly_user.sql';

# Проверить
SELECT * FROM RDB$USERS WHERE RDB$USER_NAME = 'API_READONLY';

# Выход
QUIT;
```

- [ ] Пользователь api_readonly создан
- [ ] Пароль: `Api#ReadOnly#2025!Secure`

---

## ШАГ 4: НАСТРОИТЬ .env (5 мин)

```powershell
cd C:\FirebirdAPI\firebird-db-proxy

# Скопировать шаблон
copy server-setup\env.production.example .env

# Сгенерировать токены
python scripts\generate_token.py --count 2

# Отредактировать .env
notepad .env
```

**В .env изменить:**
```env
DB_HOST=127.0.0.1  ← ВАЖНО: localhost!
DB_USER=api_readonly  ← ВАЖНО: не SYSDBA!
DB_PASSWORD=Api#ReadOnly#2025!Secure
API_TOKENS=<вставить сгенерированные токены>
```

- [ ] .env создан
- [ ] Токены сгенерированы и вставлены
- [ ] DB_HOST=127.0.0.1 (localhost)
- [ ] DB_USER=api_readonly

---

## ШАГ 5: ТЕСТ ПОДКЛЮЧЕНИЯ (2 мин)

```powershell
python scripts\test_connection.py
```

**Ожидаем:**
```
✓ Подключение успешно!
✓ Найдено таблиц: 362
ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! ✓
```

- [ ] Тест пройден ✅

**Если ошибка:**
- Проверить .env файл
- Проверить что Firebird работает
- Проверить что пользователь api_readonly создан

---

## ШАГ 6: ТЕСТ API ВРУЧНУЮ (5 мин)

```powershell
# Запустить API
python -m app.main

# В ДРУГОМ окне PowerShell:
Invoke-WebRequest http://localhost:8000/api/health
```

**Ожидаем:**
```
StatusCode : 200
```

- [ ] API запускается
- [ ] Health check работает
- [ ] В логах "Database connection test: SUCCESS ✓"

**Остановить:** CTRL+C в первом окне

---

## ШАГ 7: УСТАНОВИТЬ WINDOWS SERVICE (10 мин)

```powershell
# Запустить скрипт установки сервиса
.\server-setup\install_service.ps1

# Проверить статус
Get-Service FirebirdAPI
```

**Ожидаем:**
```
Status: Running
StartType: Automatic
```

- [ ] Windows Service создан
- [ ] Статус: Running
- [ ] Автозапуск: Enabled

---

## ШАГ 8: ОТКРЫТЬ ПОРТ В FIREWALL (3 мин)

```powershell
# Создать правило (если скрипт не создал)
New-NetFirewallRule -DisplayName "Firebird Database Proxy API" `
  -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# Проверить
Get-NetFirewallRule -DisplayName "Firebird Database Proxy API"
```

- [ ] Firewall правило создано
- [ ] Enabled: True

---

## ШАГ 9: ФИНАЛЬНАЯ ПРОВЕРКА (5 мин)

```powershell
# Запустить полную проверку
.\server-setup\verify_installation.ps1
```

**Ожидаем:**
```
🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! 🎉
```

- [ ] Все проверки пройдены

---

## ШАГ 10: ТЕСТ ИЗ ИНТЕРНЕТА (3 мин)

**С другого компьютера (не с сервера!):**

```powershell
# Health check
Invoke-WebRequest http://85.114.224.45:8000/api/health

# Swagger UI в браузере
# http://85.114.224.45:8000/docs
```

- [ ] API доступен по внешнему IP
- [ ] Swagger UI открывается

---

## ШАГ 11: ТЕСТ С ТОКЕНОМ (5 мин)

```powershell
$token = "ВАШ_ТОКЕН_ИЗ_ENV"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Получить список таблиц
Invoke-WebRequest -Uri "http://85.114.224.45:8000/api/tables" `
  -Headers $headers -UseBasicParsing

# Выполнить запрос
$body = '{"query": "SELECT COUNT(*) FROM STORGRP"}' 
Invoke-WebRequest -Uri "http://85.114.224.45:8000/api/query" `
  -Method POST -Headers $headers -Body $body -UseBasicParsing
```

- [ ] Список таблиц получен
- [ ] Запрос выполнен
- [ ] Данные возвращены

---

## ✅ ГОТОВО!

**Если все чекбоксы отмечены - установка успешна!**

### Что теперь работает:

✅ API запущен на порту 8000  
✅ Доступен из интернета: `http://85.114.224.45:8000`  
✅ Автозапуск при старте сервера  
✅ Защищен Bearer Token  
✅ Только READ-ONLY доступ к БД  
✅ Кеширование запросов  
✅ Логирование всех операций  

### Адреса для клиентов:

```
API URL: http://85.114.224.45:8000/api/query
Документация: http://85.114.224.45:8000/docs
Health check: http://85.114.224.45:8000/api/health
```

### Токены для клиентов:

**Сохранены в:** `C:\FirebirdAPI\firebird-db-proxy\.env`

```env
API_TOKENS=токен1,токен2
```

Раздайте эти токены сотрудникам для подключения!

---

## 🔧 УПРАВЛЕНИЕ

```powershell
# Остановить
Stop-Service FirebirdAPI

# Запустить
Start-Service FirebirdAPI

# Перезапустить
Restart-Service FirebirdAPI

# Статус
Get-Service FirebirdAPI

# Логи
Get-Content C:\FirebirdAPI\logs\api-output.log -Tail 50
```

---

## 📞 ПОДДЕРЖКА

**При проблемах:**
1. Проверить логи: `C:\FirebirdAPI\logs\api-error.log`
2. Перезапустить сервис: `Restart-Service FirebirdAPI`
3. Запустить проверку: `.\server-setup\verify_installation.ps1`

**Контакты:**
- GitHub: https://github.com/IvanBondarenkoIT/firebird-db-proxy
- Email: ivan.bondarenko.it@gmail.com

---

**Дата:** 21 октября 2025  
**Версия:** 1.0  
**Статус:** ✅ Готово к использованию

