Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Starting DAV Backend Platform (Port 8000)  " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Set-Location -Path (Join-Path $PSScriptRoot "backend")
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
