# Builds import-ready/*.html with CSS inlined for Figma (html.to.design)
$here = $PSScriptRoot
$css = Get-Content "$here\styles.css" -Raw
$css = $css -replace '@import\s+url\([^)]+\)\s*;', ''

$fontLinks = @'
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
'@

$outDir = Join-Path $here "import-ready"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Get-ChildItem "$here\*.html" | Where-Object { $_.Name -ne "index.html" } | ForEach-Object {
    $html = Get-Content $_.FullName -Raw
    $inlined = $html -replace '<link rel="stylesheet" href="styles.css"\s*/>', "<style>`n$css`n</style>`n$fontLinks"
    $dest = Join-Path $outDir $_.Name
    Set-Content -Path $dest -Value $inlined -Encoding UTF8
    Write-Host "Built: import-ready\$($_.Name)"
}

# Index for import-ready folder
@'
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><title>Fixora import-ready</title></head>
<body style="font-family:system-ui;background:#111;color:#eee;padding:40px">
<h1>Import-ready (CSS inlined)</h1>
<p>Use these URLs with html.to.design after running <code>start-server.ps1</code></p>
<ul>
<li><a href="01-login.html">01-login</a></li>
<li><a href="02-dashboard.html">02-dashboard</a></li>
<li><a href="03-logs.html">03-logs</a></li>
<li><a href="04-alerts.html">04-alerts</a></li>
<li><a href="05-query.html">05-query</a></li>
<li><a href="06-diagnostics.html">06-diagnostics</a></li>
<li><a href="07-enterprise.html">07-enterprise</a></li>
<li><a href="08-settings.html">08-settings</a></li>
</ul>
</body>
</html>
'@ | Set-Content (Join-Path $outDir "index.html") -Encoding UTF8

Write-Host "`nDone. Run: .\start-server.ps1"
