# Fixora - load database/schema.sql into MySQL and seed demo users
# Requires: MySQL 8 running locally (or Docker mysql container on port 3306)
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot | Split-Path -Parent

function Find-Python {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return @{ Exe = "py"; Args = @("-3") } }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python -and $python.Source -notmatch "WindowsApps") {
        return @{ Exe = $python.Source; Args = @() }
    }
    return $null
}

function Find-MySql {
    $mysql = Get-Command mysql -ErrorAction SilentlyContinue
    if ($mysql) { return $mysql.Source }
    $paths = @(
        "$env:ProgramFiles\MySQL\MySQL Server 8.0\bin\mysql.exe",
        "$env:ProgramFiles\MySQL\MySQL Server 8.4\bin\mysql.exe",
        "${env:ProgramFiles(x86)}\MySQL\MySQL Server 8.0\bin\mysql.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

if (-not (Test-Path "$Root\.env")) {
    Copy-Item "$Root\.env.example" "$Root\.env"
}

# Read MySQL settings from .env
$envFile = Get-Content "$Root\.env" -Raw
function Get-EnvValue([string]$Name, [string]$Default) {
    if ($envFile -match "(?m)^$Name=(.+)$") { return $Matches[1].Trim() }
    return $Default
}

$mysqlHost = Get-EnvValue "MYSQL_HOST" "localhost"
$mysqlPort = Get-EnvValue "MYSQL_PORT" "3306"
$mysqlUser = Get-EnvValue "MYSQL_USER" "fixora"
$mysqlPass = Get-EnvValue "MYSQL_PASSWORD" "fixora_dev_password"
$mysqlDb   = Get-EnvValue "MYSQL_DATABASE" "fixora"

$mysqlExe = Find-MySql
if (-not $mysqlExe) {
    Write-Host ""
    Write-Host "mysql client not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install MySQL 8 from https://dev.mysql.com/downloads/installer/" -ForegroundColor Cyan
    Write-Host "Or start Docker MySQL only:" -ForegroundColor Cyan
    Write-Host "  docker compose up -d mysql" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script again, or follow database/MANUAL_SETUP.md" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "=== Fixora MySQL setup ===" -ForegroundColor Cyan
Write-Host "Host: $mysqlHost`:$mysqlPort"
Write-Host "User: $mysqlUser"
Write-Host "Database: $mysqlDb"
Write-Host ""

# Test connection
$testArgs = @("-h", $mysqlHost, "-P", $mysqlPort, "-u", $mysqlUser, "-p$mysqlPass", "-e", "SELECT 1;")
& $mysqlExe @testArgs 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Cannot connect as '$mysqlUser'. Try as root first:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  mysql -u root -p < database\create_mysql_user.sql" -ForegroundColor White
    Write-Host "  mysql -u root -p < database\schema.sql" -ForegroundColor White
    Write-Host ""
    Write-Host "Or see database/MANUAL_SETUP.md" -ForegroundColor Gray
    exit 1
}

Write-Host "Loading schema.sql..."
$schemaPath = Join-Path $Root "database\schema.sql"
Get-Content $schemaPath -Raw | & $mysqlExe -h $mysqlHost -P $mysqlPort -u $mysqlUser -p$mysqlPass
if ($LASTEXITCODE -ne 0) {
    Write-Host "schema.sql failed. See errors above." -ForegroundColor Red
    exit 1
}

Write-Host "Schema loaded." -ForegroundColor Green

# Point app at MySQL (not SQLite)
$lines = Get-Content "$Root\.env"
$updated = $false
$newLines = foreach ($line in $lines) {
    if ($line -match "^USE_SQLITE=") {
        $updated = $true
        "USE_SQLITE=false"
    } else {
        $line
    }
}
if (-not $updated) { $newLines += "USE_SQLITE=false" }
$newLines | Set-Content "$Root\.env" -Encoding utf8

$env:USE_SQLITE = "false"
$env:MYSQL_HOST = $mysqlHost
$env:MYSQL_PORT = $mysqlPort
$env:MYSQL_USER = $mysqlUser
$env:MYSQL_PASSWORD = $mysqlPass
$env:MYSQL_DATABASE = $mysqlDb

$PythonInfo = Find-Python
if (-not $PythonInfo) {
    Write-Host "Python not found. Schema is loaded; run seed manually:" -ForegroundColor Yellow
    Write-Host "  `$env:USE_SQLITE='false'; py -3 scripts\seed_admin.py" -ForegroundColor White
    exit 0
}

Write-Host "Seeding demo users (admin@fixora.local / admin123)..."
$pyArgs = $PythonInfo.Args + @("$Root\scripts\seed_admin.py")
& $PythonInfo.Exe @pyArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Done. MySQL is ready." -ForegroundColor Green
Write-Host ""
Write-Host "Start the app (MySQL mode):" -ForegroundColor Cyan
Write-Host "  Terminal 1: cd backend; `$env:USE_SQLITE='false'; py -3 -m uvicorn app.main:app --reload --port 8000" -ForegroundColor White
Write-Host "  Terminal 2: cd frontend; npm run dev" -ForegroundColor White
Write-Host "  Browser:    http://localhost:5173" -ForegroundColor White
Write-Host ""
