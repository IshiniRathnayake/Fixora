# Fixora - run WITHOUT Docker (SQLite + Python + Node)
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

function Test-PythonWorks([string]$Exe) {
    if (-not $Exe -or -not (Test-Path $Exe)) { return $false }
    # Windows Store stub lives in WindowsApps and often fails
    if ($Exe -match "WindowsApps\\python") { return $false }
    try {
        $out = & $Exe --version 2>&1
        return $LASTEXITCODE -eq 0 -and ($out -match "Python 3\.\d+")
    } catch {
        return $false
    }
}

function Find-Python {
    $candidates = @()

    # py launcher (best on Windows when Python is properly installed)
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { $candidates += @("py", "-3") }

    foreach ($name in @("python3", "python")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { $candidates += ,@($cmd.Source) }
    }

    # Common install locations
    $glob = @(
        "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
        "$env:ProgramFiles\Python*\python.exe",
        "${env:ProgramFiles(x86)}\Python*\python.exe"
    )
    foreach ($pattern in $glob) {
        $candidates += @(Get-Item $pattern -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | ForEach-Object { $_.FullName })
    }

    foreach ($c in $candidates) {
        if ($c -is [array]) {
            if ($c[0] -eq "py") {
                try {
                    $v = & py -3 --version 2>&1
                    if ($LASTEXITCODE -eq 0) { return @{ Exe = "py"; Args = @("-3") } }
                } catch { }
            }
        } elseif (Test-PythonWorks $c) {
            return @{ Exe = $c; Args = @() }
        }
    }
    return $null
}

function Invoke-Python($PythonInfo, [string[]]$PythonArgs) {
    $all = $PythonInfo.Args + $PythonArgs
    & $PythonInfo.Exe @all
    if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

function Find-Npm {
    $npm = Get-Command npm -ErrorAction SilentlyContinue
    if ($npm) { return $npm.Source }
    return $null
}

$PythonInfo = Find-Python
$Npm = Find-Npm

if (-not $PythonInfo) {
    Write-Host ""
    Write-Host "Python 3 is not installed correctly on this PC." -ForegroundColor Red
    Write-Host ""
    Write-Host "The 'python' command in WindowsApps is only a Store shortcut - not real Python." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Fix (choose one):" -ForegroundColor Cyan
    Write-Host "  1. Install Python 3.12 from https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "     - Check 'Add python.exe to PATH'" -ForegroundColor Gray
    Write-Host "     - Check 'Install py launcher'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Disable the fake alias:" -ForegroundColor White
    Write-Host '     Settings - Apps - Advanced app settings - App execution aliases' -ForegroundColor Gray
    Write-Host "     Turn OFF 'python.exe' and 'python3.exe'" -ForegroundColor Gray
    Write-Host "     Then install Python from python.org" -ForegroundColor Gray
    Write-Host ""
    Write-Host "After install, close PowerShell, open a NEW window, then run:" -ForegroundColor Cyan
    Write-Host "  .\run-local.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

if (-not $Npm) {
    Write-Host ""
    Write-Host "Node.js/npm not found. Install from https://nodejs.org/" -ForegroundColor Red
    Write-Host ""
    exit 1
}

if (-not (Test-Path "$Root\.env")) {
    Copy-Item "$Root\.env.example" "$Root\.env"
}

$envContent = Get-Content "$Root\.env" -Raw -ErrorAction SilentlyContinue
if ($envContent -notmatch "USE_SQLITE") {
    Add-Content "$Root\.env" "`nUSE_SQLITE=true"
}
$env:USE_SQLITE = "true"

Write-Host ""
Write-Host "=== Fixora local mode (no Docker) ===" -ForegroundColor Cyan
Write-Host "Database: SQLite (backend/data/fixora.db)"
Write-Host "Python:   $($PythonInfo.Exe) $($PythonInfo.Args -join ' ')"
Write-Host ""

Write-Host "Installing Python dependencies (first run may take a few minutes)..."
Set-Location "$Root\backend"
Invoke-Python $PythonInfo @("-m", "pip", "install", "-r", "requirements.txt")

New-Item -ItemType Directory -Force -Path "$Root\backend\data" | Out-Null

Write-Host "Initializing database and demo users..."
Set-Location $Root
Invoke-Python $PythonInfo @("$Root\scripts\seed_admin.py")

Write-Host "Installing frontend dependencies..."
Set-Location "$Root\frontend"
if (-not (Test-Path "node_modules")) {
    & npm install
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

Write-Host ""
Write-Host "Starting API (8000) and UI (5173)..." -ForegroundColor Green
Write-Host "  http://localhost:5173  -  admin@fixora.local / admin123" -ForegroundColor White
Write-Host ""

$pyExe = $PythonInfo.Exe
$pyArg = ($PythonInfo.Args + @("-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000")) -join " "

Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$Root\backend'; `$env:USE_SQLITE='true'; & '$pyExe' $pyArg"
)

Start-Sleep -Seconds 3

Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$Root\frontend'; npm run dev"
)

Set-Location $Root
Write-Host "Done. Open http://localhost:5173" -ForegroundColor Green
