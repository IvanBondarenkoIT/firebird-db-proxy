# ============================================================
# ПРОВЕРКА УСТАНОВКИ FIREBIRD API
# ============================================================
#
# Этот скрипт проверяет что все компоненты установлены правильно.
#
# Использование:
#   .\verify_installation.ps1
#
# ============================================================

param(
    [string]$InstallPath = "C:\FirebirdAPI",
    [string]$ServiceName = "FirebirdAPI",
    [int]$ApiPort = 8000,
    [string]$ServerIP = "85.114.224.45"
)

$ErrorCount = 0
$WarningCount = 0

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "ПРОВЕРКА УСТАНОВКИ FIREBIRD API" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# ============================================================
# 1. ПРОВЕРКА PYTHON
# ============================================================

Write-Host "1. Проверка Python..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Python не найден!" -ForegroundColor Red
    $ErrorCount++
}

# ============================================================
# 2. ПРОВЕРКА ФАЙЛОВ ПРОЕКТА
# ============================================================

Write-Host "`n2. Проверка файлов проекта..." -ForegroundColor Yellow

$projectPath = Join-Path $InstallPath "firebird-db-proxy"
$requiredFiles = @(
    "app\main.py",
    "app\database.py",
    "app\config.py",
    ".env",
    "requirements.txt",
    "venv\Scripts\python.exe"
)

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $projectPath $file
    if (Test-Path $fullPath) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "   ✗ ОТСУТСТВУЕТ: $file" -ForegroundColor Red
        $ErrorCount++
    }
}

# ============================================================
# 3. ПРОВЕРКА .env КОНФИГУРАЦИИ
# ============================================================

Write-Host "`n3. Проверка .env конфигурации..." -ForegroundColor Yellow

$envPath = Join-Path $projectPath ".env"

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    
    # Проверка DB_HOST
    if ($envContent -match "DB_HOST=(127\.0\.0\.1|localhost)") {
        Write-Host "   ✓ DB_HOST использует localhost" -ForegroundColor Green
    } else {
        Write-Host "   ✗ DB_HOST должен быть 127.0.0.1 или localhost!" -ForegroundColor Red
        $ErrorCount++
    }
    
    # Проверка DB_USER
    if ($envContent -match "DB_USER=api_readonly") {
        Write-Host "   ✓ DB_USER использует api_readonly" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ DB_USER не api_readonly (проверьте безопасность!)" -ForegroundColor Yellow
        $WarningCount++
    }
    
    # Проверка токенов
    if ($envContent -match "API_TOKENS=.{64,}") {
        Write-Host "   ✓ API_TOKENS настроены" -ForegroundColor Green
    } else {
        Write-Host "   ✗ API_TOKENS не настроены или слишком короткие!" -ForegroundColor Red
        $ErrorCount++
    }
    
    # Проверка APP_ENV
    if ($envContent -match "APP_ENV=production") {
        Write-Host "   ✓ APP_ENV=production" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ APP_ENV не production" -ForegroundColor Yellow
        $WarningCount++
    }
}

# ============================================================
# 4. ПРОВЕРКА FIREBIRD
# ============================================================

Write-Host "`n4. Проверка Firebird БД..." -ForegroundColor Yellow

$firebirdTest = Test-NetConnection -ComputerName localhost -Port 3055 -WarningAction SilentlyContinue

if ($firebirdTest.TcpTestSucceeded) {
    Write-Host "   ✓ Firebird отвечает на порту 3055" -ForegroundColor Green
} else {
    Write-Host "   ✗ Firebird не доступен на localhost:3055!" -ForegroundColor Red
    $ErrorCount++
}

# ============================================================
# 5. ПРОВЕРКА WINDOWS SERVICE
# ============================================================

Write-Host "`n5. Проверка Windows Service..." -ForegroundColor Yellow

$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue

if ($service) {
    if ($service.Status -eq "Running") {
        Write-Host "   ✓ Сервис $ServiceName запущен" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Сервис $ServiceName НЕ запущен (Status: $($service.Status))" -ForegroundColor Red
        $ErrorCount++
    }
    
    if ($service.StartType -eq "Automatic") {
        Write-Host "   ✓ Автозапуск включен" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Автозапуск выключен" -ForegroundColor Yellow
        $WarningCount++
    }
} else {
    Write-Host "   ✗ Сервис $ServiceName не найден!" -ForegroundColor Red
    $ErrorCount++
}

# ============================================================
# 6. ПРОВЕРКА WINDOWS FIREWALL
# ============================================================

Write-Host "`n6. Проверка Windows Firewall..." -ForegroundColor Yellow

$firewallRule = Get-NetFirewallRule -DisplayName "Firebird Database Proxy API" -ErrorAction SilentlyContinue

if ($firewallRule) {
    if ($firewallRule.Enabled -eq "True") {
        Write-Host "   ✓ Firewall правило создано и активно" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Firewall правило создано но отключено" -ForegroundColor Yellow
        $WarningCount++
    }
} else {
    Write-Host "   ✗ Firewall правило не найдено!" -ForegroundColor Red
    $ErrorCount++
}

# Проверка порта
$portTest = Get-NetTCPConnection -LocalPort $ApiPort -ErrorAction SilentlyContinue

if ($portTest) {
    Write-Host "   ✓ Порт $ApiPort слушается" -ForegroundColor Green
} else {
    Write-Host "   ✗ Порт $ApiPort не слушается!" -ForegroundColor Red
    $ErrorCount++
}

# ============================================================
# 7. ПРОВЕРКА API (ЛОКАЛЬНО)
# ============================================================

Write-Host "`n7. Проверка API (localhost)..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:$ApiPort/api/health" -UseBasicParsing -TimeoutSec 10
    
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Health check работает" -ForegroundColor Green
        
        $health = $response.Content | ConvertFrom-Json
        
        if ($health.database_connected) {
            Write-Host "   ✓ База данных подключена" -ForegroundColor Green
        } else {
            Write-Host "   ✗ База данных НЕ подключена!" -ForegroundColor Red
            $ErrorCount++
        }
        
        Write-Host "   ✓ Версия: $($health.version)" -ForegroundColor Green
        Write-Host "   ✓ Uptime: $([math]::Round($health.uptime_seconds/60, 1)) минут" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ API не отвечает на localhost!" -ForegroundColor Red
    Write-Host "     Ошибка: $_" -ForegroundColor Gray
    $ErrorCount++
}

# ============================================================
# 8. ПРОВЕРКА API (ВНЕШНИЙ IP)
# ============================================================

Write-Host "`n8. Проверка API (внешний IP)..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://${ServerIP}:$ApiPort/api/health" -UseBasicParsing -TimeoutSec 10
    
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ API доступен по внешнему IP!" -ForegroundColor Green
        Write-Host "   ✓ URL: http://${ServerIP}:$ApiPort" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ API НЕ доступен по внешнему IP!" -ForegroundColor Red
    Write-Host "     Проверьте Windows Firewall" -ForegroundColor Yellow
    $ErrorCount++
}

# ============================================================
# 9. ПРОВЕРКА SWAGGER UI
# ============================================================

Write-Host "`n9. Проверка документации..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:$ApiPort/docs" -UseBasicParsing -TimeoutSec 10
    
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Swagger UI доступен" -ForegroundColor Green
        Write-Host "     http://${ServerIP}:$ApiPort/docs" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Swagger UI не доступен" -ForegroundColor Red
    $ErrorCount++
}

# ============================================================
# 10. ПРОВЕРКА ЛОГОВ
# ============================================================

Write-Host "`n10. Проверка логов..." -ForegroundColor Yellow

$logFiles = @(
    (Join-Path $logsPath "api-output.log"),
    (Join-Path $logsPath "api-error.log")
)

foreach ($logFile in $logFiles) {
    if (Test-Path $logFile) {
        $size = (Get-Item $logFile).Length
        Write-Host "   ✓ $(Split-Path $logFile -Leaf) ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ $(Split-Path $logFile -Leaf) не найден" -ForegroundColor Yellow
        $WarningCount++
    }
}

# ============================================================
# ИТОГОВЫЙ ОТЧЕТ
# ============================================================

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "РЕЗУЛЬТАТЫ ПРОВЕРКИ" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

if ($ErrorCount -eq 0 -and $WarningCount -eq 0) {
    Write-Host "🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! 🎉`n" -ForegroundColor Green
    
    Write-Host "API готов к использованию!`n" -ForegroundColor Green
    
    Write-Host "Доступ из интернета:" -ForegroundColor White
    Write-Host "  URL: http://${ServerIP}:$ApiPort" -ForegroundColor Cyan
    Write-Host "  Документация: http://${ServerIP}:$ApiPort/docs`n" -ForegroundColor Cyan
    
    Write-Host "Для подключения клиентов:" -ForegroundColor White
    Write-Host "  1. Раздайте токены из .env файла" -ForegroundColor Gray
    Write-Host "  2. Используйте URL: http://${ServerIP}:$ApiPort/api/query" -ForegroundColor Gray
    Write-Host "  3. Добавьте заголовок: Authorization: Bearer ТОКЕН`n" -ForegroundColor Gray
    
} elseif ($ErrorCount -eq 0) {
    Write-Host "⚠ ЕСТЬ ПРЕДУПРЕЖДЕНИЯ ($WarningCount)`n" -ForegroundColor Yellow
    Write-Host "API работает, но есть моменты для улучшения.`n" -ForegroundColor Yellow
} else {
    Write-Host "✗ НАЙДЕНЫ ОШИБКИ: $ErrorCount" -ForegroundColor Red
    Write-Host "⚠ Предупреждения: $WarningCount`n" -ForegroundColor Yellow
    Write-Host "Проверьте логи и исправьте ошибки перед использованием.`n" -ForegroundColor Red
}

Write-Host "Логи сервиса:" -ForegroundColor White
Write-Host "  Get-Content '$logsPath\api-output.log' -Tail 50`n" -ForegroundColor Gray

Write-Host "Управление сервисом:" -ForegroundColor White
Write-Host "  Start-Service $ServiceName" -ForegroundColor Gray
Write-Host "  Stop-Service $ServiceName" -ForegroundColor Gray
Write-Host "  Restart-Service $ServiceName`n" -ForegroundColor Gray

Write-Host "============================================================`n" -ForegroundColor Cyan

exit $ErrorCount

