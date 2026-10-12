Write-Host "=============================================" -ForegroundColor Green
Write-Host "   Starting DAV Frontend App (Port 5173)     " -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Set-Location -Path (Join-Path $PSScriptRoot "frontend")
npm.cmd run dev
