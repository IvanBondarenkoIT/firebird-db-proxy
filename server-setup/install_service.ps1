# ============================================================
# УСТАНОВКА FIREBIRD API КАК WINDOWS SERVICE
# ============================================================
#
# Этот скрипт устанавливает API как Windows Service для автозапуска.
# Запускать от имени Администратора!
#
# Использование:
#   .\install_service.ps1
#
# ============================================================

param(
    [string]$InstallPath = "C:\FirebirdAPI",
    [string]$ServiceName = "FirebirdAPI"
)

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "УСТАНОВКА WINDOWS SERVICE" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "✗ ОШИБКА: Требуются права администратора!" -ForegroundColor Red
    exit 1
}

$projectPath = Join-Path $InstallPath "firebird-db-proxy"
$nssmPath = Join-Path $InstallPath "nssm.exe"
$pythonPath = Join-Path $projectPath "venv\Scripts\python.exe"
$logsPath = Join-Path $InstallPath "logs"

# ============================================================
# 1. СКАЧАТЬ NSSM
# ============================================================

Write-Host "Шаг 1: Установка NSSM..." -ForegroundColor Yellow

if (-not (Test-Path $nssmPath)) {
    Write-Host "  Скачиваем NSSM..." -ForegroundColor Gray
    
    try {
        Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" `
            -OutFile "$env:TEMP\nssm.zip" -UseBasicParsing
        
        Expand-Archive -Path "$env:TEMP\nssm.zip" -DestinationPath "$env:TEMP\nssm" -Force
        Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" $nssmPath
        
        Write-Host "✓ NSSM установлен" -ForegroundColor Green
    } catch {
        Write-Host "✗ Ошибка скачивания NSSM: $_" -ForegroundColor Red
        Write-Host "  Скачайте вручную с https://nssm.cc/download" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✓ NSSM уже установлен" -ForegroundColor Green
}

# ============================================================
# 2. УДАЛИТЬ СУЩЕСТВУЮЩИЙ СЕРВИС (если есть)
# ============================================================

Write-Host "`nШаг 2: Проверка существующего сервиса..." -ForegroundColor Yellow

$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue

if ($existingService) {
    Write-Host "  Найден существующий сервис, удаляем..." -ForegroundColor Gray
    
    Stop-Service $ServiceName -ErrorAction SilentlyContinue
    & $nssmPath remove $ServiceName confirm
    
    Write-Host "✓ Старый сервис удален" -ForegroundColor Green
}

# ============================================================
# 3. УСТАНОВИТЬ НОВЫЙ СЕРВИС
# ============================================================

Write-Host "`nШаг 3: Создание Windows Service..." -ForegroundColor Yellow

# Установить сервис
& $nssmPath install $ServiceName $pythonPath "-m" "app.main"

# Настроить параметры
& $nssmPath set $ServiceName AppDirectory $projectPath
& $nssmPath set $ServiceName DisplayName "Firebird Database Proxy API"
& $nssmPath set $ServiceName Description "REST API для безопасного доступа к Firebird БД"
& $nssmPath set $ServiceName Start SERVICE_AUTO_START

# Настроить логирование
& $nssmPath set $ServiceName AppStdout "$logsPath\api-output.log"
& $nssmPath set $ServiceName AppStderr "$logsPath\api-error.log"

# Настроить автоперезапуск при сбоях
& $nssmPath set $ServiceName AppExit Default Restart
& $nssmPath set $ServiceName AppRestartDelay 5000

Write-Host "✓ Windows Service создан" -ForegroundColor Green

# ============================================================
# 4. ЗАПУСТИТЬ СЕРВИС
# ============================================================

Write-Host "`nШаг 4: Запуск сервиса..." -ForegroundColor Yellow

Start-Service $ServiceName

# Подождать немного
Start-Sleep -Seconds 3

$service = Get-Service $ServiceName

if ($service.Status -eq "Running") {
    Write-Host "✓ Сервис запущен успешно!" -ForegroundColor Green
} else {
    Write-Host "✗ Сервис не запустился!" -ForegroundColor Red
    Write-Host "  Проверьте логи: $logsPath\api-error.log" -ForegroundColor Yellow
    exit 1
}

# ============================================================
# 5. ПРОВЕРКА РАБОТЫ
# ============================================================

Write-Host "`nШаг 5: Проверка работы API..." -ForegroundColor Yellow

Start-Sleep -Seconds 2

try {
    $response = Invoke-WebRequest -Uri "http://localhost:$ApiPort/api/health" -UseBasicParsing -TimeoutSec 10
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API отвечает на health check!" -ForegroundColor Green
        
        $health = $response.Content | ConvertFrom-Json
        Write-Host "  Status: $($health.status)" -ForegroundColor Gray
        Write-Host "  Database connected: $($health.database_connected)" -ForegroundColor Gray
        Write-Host "  Version: $($health.version)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ API не отвечает!" -ForegroundColor Red
    Write-Host "  Проверьте логи: $logsPath\api-error.log" -ForegroundColor Yellow
}

# ============================================================
# ИТОГО
# ============================================================

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "УСТАНОВКА ЗАВЕРШЕНА!" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Сервис:" -ForegroundColor White
Write-Host "  Имя: $ServiceName" -ForegroundColor Gray
Write-Host "  Статус: Running" -ForegroundColor Green
Write-Host "  Автозапуск: Enabled`n" -ForegroundColor Green

Write-Host "API доступен:" -ForegroundColor White
Write-Host "  Локально: http://localhost:$ApiPort" -ForegroundColor Gray
Write-Host "  Документация: http://localhost:$ApiPort/docs`n" -ForegroundColor Gray

Write-Host "Логи:" -ForegroundColor White
Write-Host "  Output: $logsPath\api-output.log" -ForegroundColor Gray
Write-Host "  Errors: $logsPath\api-error.log`n" -ForegroundColor Gray

Write-Host "СЛЕДУЮЩИЕ ШАГИ:" -ForegroundColor Yellow
Write-Host "  1. Проверьте работу: .\server-setup\verify_installation.ps1" -ForegroundColor White
Write-Host "  2. Раздайте токены пользователям" -ForegroundColor White
Write-Host "  3. Протестируйте из другого города/офиса`n" -ForegroundColor White

Write-Host "============================================================`n" -ForegroundColor Cyan

