# ⚡ Быстрый перезапуск сервиса

## 🔍 Сначала проверьте статус

```powershell
Get-Service FirebirdAPI
```

**Если сервис не найден** - он не установлен, нужно установить заново.

---

## 🚀 Перезапуск (если сервис существует)

### Вариант 1: Простой перезапуск

**⚠️ Требуются права администратора!**

```powershell
Restart-Service FirebirdAPI
```

### Вариант 2: С проверкой (рекомендуется)

```powershell
# Остановить
Stop-Service FirebirdAPI

# Подождать
Start-Sleep -Seconds 3

# Запустить
Start-Service FirebirdAPI

# Проверить статус
Get-Service FirebirdAPI
```

**Примечание:** Если получаете ошибку "Не удалось открыть службу" - запустите PowerShell от имени администратора!

---

## ✅ Проверка после перезапуска

```powershell
# 1. Проверить что сервис запущен
Get-Service FirebirdAPI

# 2. Проверить что API отвечает
Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing
```

**Ожидаемый результат:**
- Статус сервиса: `Running`
- Health check: статус код `200` и JSON с информацией

---

## 📋 Если не работает

Выполните полную диагностику:

```powershell
# Проверить статус
Get-Service FirebirdAPI | Format-List

# Проверить порт
Get-NetTCPConnection -LocalPort 8000

# Посмотреть последние ошибки
Get-Content "C:\FirebirdAPI\logs\api-error.log" -Tail 20
```

---

## 🔧 Если сервис не найден

Сервис нужно установить заново:

```powershell
# От администратора!
cd C:\FirebirdAPI\firebird-db-proxy
.\server-setup\install_service.ps1
```

**Примечание:** Замените путь `C:\FirebirdAPI` на ваш реальный путь, если он другой!

---

## 🆘 Альтернативные способы перезапуска

### Через NSSM (если установлен)

```powershell
C:\FirebirdAPI\nssm.exe restart FirebirdAPI
```

### Через графический интерфейс

1. Нажмите `Win + R`
2. Введите `services.msc` и нажмите Enter
3. Найдите "Firebird Database Proxy API"
4. Правой кнопкой → "Перезапустить"

