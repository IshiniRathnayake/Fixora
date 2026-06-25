# Quick check: Python, Node, Docker
Write-Host "Fixora prerequisite check`n" -ForegroundColor Cyan

$fakePython = "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe"
if (Test-Path $fakePython) {
    Write-Host "[!] Windows Store python alias exists (often breaks real Python)" -ForegroundColor Yellow
    Write-Host '    Disable in: Settings - Apps - App execution aliases' -ForegroundColor Gray
    Write-Host ""
}

foreach ($cmd in @("py -3 --version", "python --version", "node --version", "npm --version", "docker --version")) {
    try {
        $r = Invoke-Expression $cmd 2>&1
        if ($LASTEXITCODE -eq 0 -or $r) {
            Write-Host "[OK] $cmd : $r" -ForegroundColor Green
        } else {
            Write-Host "[--] $cmd" -ForegroundColor Red
        }
    } catch {
        Write-Host "[--] $cmd (not found)" -ForegroundColor Red
    }
}

Write-Host "`nIf Python fails: install from https://www.python.org/downloads/" -ForegroundColor Cyan
