# Local server for Figma html.to.design import (CSS + fonts load over HTTP)
$here = $PSScriptRoot

if (-not (Test-Path "$here\import-ready\01-login.html")) {
    Write-Host "Building import-ready pages first..."
    & "$here\build-import-ready.ps1"
}

Set-Location "$here\import-ready"
Write-Host ""
Write-Host "Server starting. Import THESE URLs in Figma html.to.design:"
Write-Host "  http://localhost:5500/01-login.html"
Write-Host "  http://localhost:5500/02-dashboard.html"
Write-Host "  ... (through 08-settings.html)"
Write-Host ""
Write-Host "Press Ctrl+C to stop."
Write-Host ""

npx --yes serve -l 5500 .
