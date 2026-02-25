@echo off
chcp 65001 >nul
echo 正在检查依赖...
pip install -r requirements.txt -q
echo.
echo 启动微店库存监控（按 Ctrl+C 可停止）...
python nize_kms.py
pause
