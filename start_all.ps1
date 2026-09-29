Write-Host "=============================================" -ForegroundColor Yellow
Write-Host "     Launching DAV Full-Stack Platform       " -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow

$backendScript = "C:\Users\harsh\.gemini\antigravity\scratch\dav\start_backend.ps1"
$frontendScript = "C:\Users\harsh\.gemini\antigravity\scratch\dav\start_frontend.ps1"

Write-Host "1. Launching Backend in new PowerShell window..." -ForegroundColor Cyan
Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$backendScript`""

Write-Host "2. Launching Frontend in new PowerShell window..." -ForegroundColor Green
Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$frontendScript`""

Write-Host "Waiting 4 seconds for services to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 4

Write-Host "3. Opening DAV application in your default browser..." -ForegroundColor Yellow
Start-Process "http://localhost:5173"
Start-Process "http://127.0.0.1:8000/docs"

Write-Host "Both services are running!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend:  http://127.0.0.1:8000/docs" -ForegroundColor White
