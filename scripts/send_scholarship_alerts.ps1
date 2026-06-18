$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$python = "C:\Python312\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $python = "python"
}

& $python manage.py send_scholarship_alerts
