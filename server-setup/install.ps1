# ============================================================
# АВТОМАТИЧЕСКАЯ УСТАНОВКА FIREBIRD API НА WINDOWS SERVER
# ============================================================
# 
# Этот скрипт автоматизирует установку API на Windows Server.
# Запускать от имени Администратора!
#
# Использование:
#   .\install.ps1
#
# ============================================================

param(
    [string]$InstallPath = "C:\FirebirdAPI",
    [int]$ApiPort = 8000
)

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "УСТАНОВКА FIREBIRD DATABASE PROXY API" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ОШИБКА: Требуются права администратора!" -ForegroundColor Red
    Write-Host "Запустите PowerShell от имени администратора." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Права администратора подтверждены`n" -ForegroundColor Green

# ============================================================
# 1. ПРОВЕРКА PYTHON
# ============================================================

Write-Host "Шаг 1: Проверка Python..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python найден: $pythonVersion" -ForegroundColor Green
    
    # Проверка версии
    if ($pythonVersion -match "3\.13") {
        Write-Host "⚠ Предупреждение: Python 3.13 может иметь проблемы совместимости" -ForegroundColor Yellow
        Write-Host "  Рекомендуется Python 3.12 или 3.11" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Python не найден!" -ForegroundColor Red
    Write-Host "`nУстановите Python 3.12 с https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "При установке отметьте 'Add Python to PATH'" -ForegroundColor Yellow
    exit 1
}

# ============================================================
# 2. ПРОВЕРКА GIT
# ============================================================

Write-Host "`nШаг 2: Проверка Git..." -ForegroundColor Yellow

try {
    $gitVersion = git --version 2>&1
    Write-Host "✓ Git найден: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git не найден!" -ForegroundColor Red
    Write-Host "`nУстановите Git с https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# ============================================================
# 3. СОЗДАНИЕ РАБОЧЕЙ ДИРЕКТОРИИ
# ============================================================

Write-Host "`nШаг 3: Создание рабочей директории..." -ForegroundColor Yellow

if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-Host "✓ Создана директория: $InstallPath" -ForegroundColor Green
} else {
    Write-Host "✓ Директория существует: $InstallPath" -ForegroundColor Green
}

# ============================================================
# 4. КЛОНИРОВАНИЕ РЕПОЗИТОРИЯ
# ============================================================

Write-Host "`nШаг 4: Скачивание кода..." -ForegroundColor Yellow

$projectPath = Join-Path $InstallPath "firebird-db-proxy"

if (Test-Path $projectPath) {
    Write-Host "⚠ Проект уже существует, обновляем..." -ForegroundColor Yellow
    cd $projectPath
    git pull origin main
} else {
    cd $InstallPath
    git clone https://github.com/IvanBondarenkoIT/firebird-db-proxy.git
    cd firebird-db-proxy
}

Write-Host "✓ Код скачан" -ForegroundColor Green

# ============================================================
# 5. СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ
# ============================================================

Write-Host "`nШаг 5: Создание виртуального окружения..." -ForegroundColor Yellow

if (Test-Path "venv") {
    Write-Host "⚠ Виртуальное окружение существует, пересоздаем..." -ForegroundColor Yellow
    Remove-Item -Path "venv" -Recurse -Force
}

python -m venv venv
Write-Host "✓ Виртуальное окружение создано" -ForegroundColor Green

# Активировать
& .\venv\Scripts\Activate.ps1

# ============================================================
# 6. УСТАНОВКА ЗАВИСИМОСТЕЙ
# ============================================================

Write-Host "`nШаг 6: Установка зависимостей..." -ForegroundColor Yellow
Write-Host "  (это может занять 2-3 минуты)`n" -ForegroundColor Gray

python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Зависимости установлены" -ForegroundColor Green
} else {
    Write-Host "✗ Ошибка установки зависимостей!" -ForegroundColor Red
    exit 1
}

# ============================================================
# 7. СОЗДАНИЕ ПАПКИ ДЛЯ ЛОГОВ
# ============================================================

Write-Host "`nШаг 7: Создание папки для логов..." -ForegroundColor Yellow

$logsPath = Join-Path $InstallPath "logs"
New-Item -ItemType Directory -Path $logsPath -Force | Out-Null
Write-Host "✓ Папка логов: $logsPath" -ForegroundColor Green

# ============================================================
# 8. НАСТРОЙКА .env ФАЙЛА
# ============================================================

Write-Host "`nШаг 8: Настройка .env файла..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Copy-Item "server-setup\.env.production" ".env"
    Write-Host "✓ Файл .env создан из шаблона" -ForegroundColor Green
    Write-Host "`n⚠ ВАЖНО: Отредактируйте .env файл!" -ForegroundColor Yellow
    Write-Host "  1. Сгенерируйте токены: python scripts\generate_token.py --count 2" -ForegroundColor Yellow
    Write-Host "  2. Вставьте токены в .env" -ForegroundColor Yellow
    Write-Host "  3. Проверьте параметры БД" -ForegroundColor Yellow
} else {
    Write-Host "⚠ Файл .env уже существует, оставляем как есть" -ForegroundColor Yellow
}

# ============================================================
# 9. НАСТРОЙКА WINDOWS FIREWALL
# ============================================================

Write-Host "`nШаг 9: Настройка Windows Firewall..." -ForegroundColor Yellow

try {
    # Проверить существующее правило
    $existingRule = Get-NetFirewallRule -DisplayName "Firebird Database Proxy API" -ErrorAction SilentlyContinue
    
    if ($existingRule) {
        Write-Host "⚠ Правило firewall уже существует, обновляем..." -ForegroundColor Yellow
        Remove-NetFirewallRule -DisplayName "Firebird Database Proxy API"
    }
    
    # Создать новое правило
    New-NetFirewallRule -DisplayName "Firebird Database Proxy API" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort $ApiPort `
        -Action Allow `
        -Profile Any `
        -Enabled True | Out-Null
    
    Write-Host "✓ Firewall: порт $ApiPort открыт для входящих подключений" -ForegroundColor Green
} catch {
    Write-Host "✗ Ошибка настройки firewall: $_" -ForegroundColor Red
    Write-Host "  Настройте вручную через Windows Defender Firewall" -ForegroundColor Yellow
}

# ============================================================
# ЗАВЕРШЕНИЕ
# ============================================================

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "УСТАНОВКА ЗАВЕРШЕНА!" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "СЛЕДУЮЩИЕ ШАГИ:`n" -ForegroundColor Yellow

Write-Host "1. Создайте READ-ONLY пользователя в Firebird:" -ForegroundColor White
Write-Host "   isql -user SYSDBA -password masterkey localhost/3055:DK_GEORGIA" -ForegroundColor Gray
Write-Host "   Затем выполните: server-setup\create_readonly_user.sql`n" -ForegroundColor Gray

Write-Host "2. Сгенерируйте токены:" -ForegroundColor White
Write-Host "   python scripts\generate_token.py --count 2" -ForegroundColor Gray
Write-Host "   Скопируйте токены в .env файл`n" -ForegroundColor Gray

Write-Host "3. Протестируйте подключение:" -ForegroundColor White
Write-Host "   python scripts\test_connection.py`n" -ForegroundColor Gray

Write-Host "4. Установите Windows Service:" -ForegroundColor White
Write-Host "   .\server-setup\install_service.ps1`n" -ForegroundColor Gray

Write-Host "5. Проверьте работу:" -ForegroundColor White
Write-Host "   .\server-setup\verify_installation.ps1`n" -ForegroundColor Gray

Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Текущая директория: $projectPath" -ForegroundColor Gray
Write-Host "Логи будут в: $logsPath`n" -ForegroundColor Gray

