# Fixora one-time setup (Windows PowerShell)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Starting MySQL via Docker..."
Set-Location $Root
docker compose up -d mysql
Start-Sleep -Seconds 15

Write-Host "Installing backend dependencies..."
Set-Location "$Root\backend"
pip install -r requirements.txt

Write-Host "Seeding users..."
Set-Location $Root
python scripts\seed_admin.py

Write-Host ""
Write-Host "Done. Next steps:"
Write-Host "  1. Copy .env.example to .env and add XAI_API_KEY (optional)"
Write-Host "  2. docker compose up --build"
Write-Host "  3. Open http://localhost:5173"
Write-Host "     Admin: admin@fixora.local / admin123"
