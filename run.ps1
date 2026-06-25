# Fixora - start with Docker (if installed)
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

$Docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $Docker) {
    Write-Host ""
    Write-Host "Docker is not installed or not in PATH." -ForegroundColor Yellow
    Write-Host "Use local mode instead (no Docker, uses SQLite):" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  .\run-local.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Or install Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor Gray
    Write-Host ""
    & "$Root\run-local.ps1"
    exit $LASTEXITCODE
}

if (-not (Test-Path "$Root\.env")) {
    Copy-Item "$Root\.env.example" "$Root\.env"
    Write-Host "Created .env from .env.example"
}

Set-Location $Root
Write-Host "Starting Fixora (MySQL + API + UI)..."
docker compose up --build
