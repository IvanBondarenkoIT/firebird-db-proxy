# ============================================================
# УДАЛЕНИЕ FIREBIRD API
# ============================================================
#
# Этот скрипт полностью удаляет API и Windows Service.
# Запускать от имени Администратора!
#
# ============================================================

param(
    [string]$InstallPath = "C:\FirebirdAPI",
    [string]$ServiceName = "FirebirdAPI",
    [switch]$KeepLogs
)

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "УДАЛЕНИЕ FIREBIRD API" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Подтверждение
$confirm = Read-Host "Вы уверены что хотите удалить API? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "`nОтменено пользователем." -ForegroundColor Yellow
    exit 0
}

# Проверка прав
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "✗ Требуются права администратора!" -ForegroundColor Red
    exit 1
}

# Остановить и удалить сервис
Write-Host "Удаление Windows Service..." -ForegroundColor Yellow

$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service) {
    Stop-Service $ServiceName -ErrorAction SilentlyContinue
    & "C:\FirebirdAPI\nssm.exe" remove $ServiceName confirm
    Write-Host "✓ Сервис удален" -ForegroundColor Green
}

# Удалить firewall правило
Write-Host "`nУдаление Firewall правила..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "Firebird Database Proxy API" -ErrorAction SilentlyContinue
Write-Host "✓ Firewall правило удалено" -ForegroundColor Green

# Удалить файлы
if (-not $KeepLogs) {
    Write-Host "`nУдаление файлов..." -ForegroundColor Yellow
    Remove-Item -Path $InstallPath -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Файлы удалены" -ForegroundColor Green
} else {
    Write-Host "`n⚠ Логи сохранены в: $InstallPath\logs" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "УДАЛЕНИЕ ЗАВЕРШЕНО" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

