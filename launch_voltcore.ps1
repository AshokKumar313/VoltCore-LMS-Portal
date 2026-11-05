# VoltCore Apex Academia - One-Click Launcher for Windows PowerShell
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  VOLTCORE APEX ACADEMIA - ANNA UNIVERSITY / MIT CAMPUS (ECE R2023)" -ForegroundColor Green
Write-Host "  Department of Electronics Engineering | Platform Lead: Ashok Kumar A" -ForegroundColor White
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

Write-Host "[1/3] Starting Backend Telemetry & REST Server (Port 5000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python attendance_server.py"

Start-Sleep -Seconds 2

Write-Host "[2/3] Starting Frontend Astro Web Server (Port 4321)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm.cmd run preview -- --port 4321 --host"

Start-Sleep -Seconds 3

Write-Host "[3/3] Opening Google Chrome to http://localhost:4321..." -ForegroundColor Green
Start-Process "http://localhost:4321"

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  ALL SYSTEMS OPERATIONAL!" -ForegroundColor Green
Write-Host "  - Web Portal:   http://localhost:4321" -ForegroundColor White
Write-Host "  - REST Gateway: http://localhost:5000" -ForegroundColor White
Write-Host "===============================================================================" -ForegroundColor Cyan
