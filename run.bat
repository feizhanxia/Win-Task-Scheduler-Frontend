@echo off
chcp 65001 >nul
title Windows Task Scheduler Frontend

echo ================================================================
echo              Windows Task Scheduler Frontend
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found, please install Python first
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        echo Please check your internet connection or run manually: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [SUCCESS] Dependencies installed successfully
    echo.
)

REM Check if port 8501 is in use
netstat -an | find "8501" | find "LISTENING" >nul
if not errorlevel 1 (
    echo [WARNING] Port 8501 is already in use
    echo Please open in browser: http://localhost:8501
    echo Or close other programs using this port
    echo.
    pause
    exit /b 1
)

echo [STARTING] Starting Streamlit server...
echo [INFO] Browser will open automatically, if not please visit: http://localhost:8501
echo [STOP] Press Ctrl+C to stop the server
echo.
echo ================================================================

REM Open browser after 3 seconds delay
start "" /min cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:8501"

REM Start Streamlit
streamlit run app.py --server.port=8501 --server.enableCORS=false --server.enableXsrfProtection=false --browser.gatherUsageStats=false

echo.
echo ================================================================
echo                    Server stopped
echo ================================================================
pause
