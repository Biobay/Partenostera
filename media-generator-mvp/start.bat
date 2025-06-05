@echo off
title Media Generator MVP
cd /d "%~dp0"

echo ======================================
echo      MEDIA GENERATOR MVP
echo ======================================
echo.

echo Controllo Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRORE: Python non trovato!
    echo Installa Python da https://python.org
    pause
    exit /b 1
)

echo Controllo Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRORE: Node.js non trovato!
    echo Installa Node.js da https://nodejs.org
    pause
    exit /b 1
)

echo.
echo Avvio dell'applicazione...
python start.py

pause
