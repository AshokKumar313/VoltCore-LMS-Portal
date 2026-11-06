@echo off
title VoltCore Apex Academia - Mission Control
cls
echo ===============================================================================
echo   VOLTCORE APEX ACADEMIA - ANNA UNIVERSITY / MIT CAMPUS (ECE R2023)
echo   Department of Electronics Engineering ^| Platform Lead: Ashok Kumar A
echo ===============================================================================
echo.
cd /d "%~dp0"

echo [1/3] Starting Backend Telemetry & REST Server on http://localhost:5000...
start "VoltCore Backend Gateway (Port 5000)" cmd /k "python attendance_server.py"

echo [2/3] Initializing Backend Gateway...
timeout /t 2 /nobreak >nul

echo [3/3] Starting Frontend Astro Web Server on http://localhost:4321...
start "VoltCore Frontend Server (Port 4321)" cmd /k "npm.cmd run preview -- --port 4321 --host"

echo [4/4] Opening Google Chrome to http://localhost:4321...
timeout /t 3 /nobreak >nul
start "" "http://localhost:4321"

echo.
echo ===============================================================================
echo   SYSTEMS OPERATIONAL!
echo   - Web Application: http://localhost:4321
echo   - REST Gateway:    http://localhost:5000
echo   Leave the two terminal windows running while using the portal.
echo ===============================================================================
pause

