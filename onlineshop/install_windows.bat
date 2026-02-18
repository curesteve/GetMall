@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo === GetMall onlineshop - Windows 安装与运行 ===
echo.

echo [1/4] 检查 Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到 Python。请先安装 Python 3.8+ 并勾选 "Add Python to PATH"
    echo 下载: https://www.python.org/downloads/
    echo 或使用: winget install Python.Python.3.12
    pause
    exit /b 1
)
python --version
echo.

echo [2/4] 检查 Chrome 浏览器...
reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version >nul 2>&1
if %errorlevel% neq 0 (
    reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
)
if %errorlevel% neq 0 (
    echo 建议安装 Google Chrome 以运行脚本抓取数据。
    echo 下载: https://www.google.com/chrome/
    echo 继续将只配置 Python 环境...
    pause
) else (
    echo 已检测到 Chrome。
)
echo.

echo [3/4] 创建虚拟环境并安装依赖...
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败，可尝试: pip install selenium beautifulsoup4
    pause
    exit /b 1
)
echo.

echo [4/4] 运行程序...
echo 执行: python nize_kms.py
echo 无头模式请先设置: set HEADLESS=1
echo.
python nize_kms.py

pause
