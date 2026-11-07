@echo off
REM =========================================================================
REM VoltCore Apex Academia - 1-Click GitHub & Workspace Sync Wrapper
REM Department of Electronics Engineering, MIT Campus, Anna University
REM Hardware Target: HP Victus (LAPTOP-3NEGBVLE)
REM =========================================================================

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync_repo.ps1" %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Sync script terminated with exit code %ERRORLEVEL%.
    pause
)
