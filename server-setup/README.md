# 📦 ФАЙЛЫ ДЛЯ УСТАНОВКИ НА WINDOWS SERVER

Эта папка содержит все необходимые файлы для установки API на Windows Server.

---

## 📁 СОДЕРЖИМОЕ ПАПКИ

### 📜 Инструкции:

- **`../WINDOWS_SERVER_INSTALLATION.md`** - Полная пошаговая инструкция установки
- **`README.md`** - Этот файл (описание содержимого)

### 🔧 Скрипты установки:

- **`install.ps1`** - Автоматическая установка приложения
- **`install_service.ps1`** - Установка как Windows Service  
- **`verify_installation.ps1`** - Проверка правильности установки

### 📄 Конфигурационные файлы:

- **`env.production.example`** - Пример .env для production на сервере
- **`create_readonly_user.sql`** - SQL для создания READ-ONLY пользователя

---

## 🚀 БЫСТРЫЙ СТАРТ

### Вариант A: Автоматическая установка

```powershell
# 1. Открыть PowerShell от администратора
# 2. Перейти в папку проекта
cd C:\path\to\firebird-db-proxy

# 3. Запустить автоустановку
.\server-setup\install.ps1

# 4. Следовать инструкциям на экране
```

### Вариант B: Ручная установка

Следовать инструкциям в **`WINDOWS_SERVER_INSTALLATION.md`**

---

## 📋 ПОРЯДОК ДЕЙСТВИЙ

### 1. Предварительная подготовка

- [ ] Проверить Python 3.12 установлен
- [ ] Проверить Git установлен
- [ ] Подготовить доступы к серверу
- [ ] Проверить что Firebird работает

### 2. Создание READ-ONLY пользователя

```powershell
# Подключиться к Firebird как SYSDBA
isql -user SYSDBA -password masterkey localhost/3055:DK_GEORGIA

# Выполнить SQL из файла:
INPUT 'server-setup/create_readonly_user.sql';

# Проверить
SELECT * FROM RDB$USERS WHERE RDB$USER_NAME = 'API_READONLY';
```

### 3. Установка приложения

```powershell
# Запустить автоустановку
.\server-setup\install.ps1
```

Или вручную:
- Клонировать репозиторий
- Создать venv
- Установить зависимости
- Настроить .env

### 4. Настройка .env

```powershell
# Скопировать шаблон
copy server-setup\env.production.example .env

# Сгенерировать токены
python scripts\generate_token.py --count 2

# Отредактировать .env
notepad .env
```

### 5. Установка Windows Service

```powershell
.\server-setup\install_service.ps1
```

### 6. Проверка установки

```powershell
.\server-setup\verify_installation.ps1
```

Должно показать: **ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!** ✅

---

## ✅ ФИНАЛЬНАЯ ПРОВЕРКА

После установки проверьте:

```powershell
# Сервис запущен
Get-Service FirebirdAPI
# → Running

# API работает локально
Invoke-WebRequest http://localhost:8000/api/health
# → 200 OK

# API доступен из сети
Invoke-WebRequest http://85.114.224.45:8000/api/health
# → 200 OK
```

---

## 📞 ПОДДЕРЖКА

**При проблемах:**

1. Проверьте логи:
   ```powershell
   Get-Content C:\FirebirdAPI\logs\api-error.log -Tail 50
   ```

2. Запустите проверку:
   ```powershell
   .\server-setup\verify_installation.ps1
   ```

3. Смотрите полную инструкцию:
   ```
   WINDOWS_SERVER_INSTALLATION.md
   ```

---

**Дата:** 21 октября 2025  
**Версия:** 1.0

