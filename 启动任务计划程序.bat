@echo off
chcp 65001 >nul
title Windows Task Scheduler Frontend

echo ================================================================
echo              Windows Task Scheduler Frontend
echo ================================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 检查 streamlit 是否安装
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败
        echo 请检查网络连接或手动运行: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [成功] 依赖包安装完成
    echo.
)

REM 检查端口 8501 是否被占用
netstat -an | find "8501" | find "LISTENING" >nul
if not errorlevel 1 (
    echo [警告] 端口 8501 已被占用
    echo 请在浏览器中打开: http://localhost:8501
    echo 或者关闭其他占用该端口的程序
    echo.
    pause
    exit /b 1
)

echo [启动] 正在启动 Streamlit 服务器...
echo [提示] 浏览器将自动打开，如果没有请手动访问: http://localhost:8501
echo [停止] 按 Ctrl+C 停止服务器
echo.
echo ================================================================

REM 延迟 3 秒后打开浏览器
start "" /min cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:8501"

REM 启动 Streamlit
streamlit run app.py --server.port=8501 --server.enableCORS=false --server.enableXsrfProtection=false --browser.gatherUsageStats=false

echo.
echo ================================================================
echo                    服务器已停止
echo ================================================================
pause
