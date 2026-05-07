@echo off
setlocal
set BASEDIR=%~dp0

echo ============================================
echo  Hotel Management System - Baslatiliyor...
echo ============================================
echo.

:: 1) PostgreSQL (Docker)
echo [1/3] PostgreSQL Docker container baslatiliyor...
cd /d %BASEDIR%Backend
docker compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo HATA: Docker Compose calismadi. Docker Desktop'in acik olduguna emin olun.
    pause
    exit /b 1
)
echo       PostgreSQL hazir (port 5500)
echo.

:: 2) Backend + MCP Server (yeni pencerede)
echo [2/3] Backend + MCP Server baslatiliyor...
start "Backend + MCP Server" cmd /k "cd /d %BASEDIR%Backend && call .venv\Scripts\activate.bat && python run.py"
echo       Backend: http://localhost:8000
echo       MCP    : http://localhost:8001
echo.

:: 3) Frontend (yeni pencerede)
echo [3/3] Frontend baslatiliyor...
start "Frontend (Vite)" cmd /k "cd /d %BASEDIR%Frontend && npm run dev"
echo       Frontend: http://localhost:5173
echo.

echo ============================================
echo  Tum servisler baslatildi!
echo  Durdurmak icin her iki CMD penceresini
echo  kapatin, sonra: docker compose down
echo ============================================
echo.
pause
endlocal
