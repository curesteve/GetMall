# GetMall onlineshop - Windows 安装与运行（PowerShell）
# 用法：在 PowerShell 中执行 .\install_windows.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== GetMall onlineshop - Windows 安装与运行 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 Python
Write-Host "[1/4] 检查 Python..." -ForegroundColor Yellow
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "未检测到 Python。请先安装 Python 3.8+ 并勾选 Add Python to PATH" -ForegroundColor Red
    Write-Host "下载: https://www.python.org/downloads/" -ForegroundColor Gray
    Write-Host "或: winget install Python.Python.3.12" -ForegroundColor Gray
    exit 1
}
python --version
Write-Host ""

# 2. 检查 Chrome（可选提示）
Write-Host "[2/4] 检查 Chrome 浏览器..." -ForegroundColor Yellow
$chrome = Test-Path "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe" -or
          Test-Path "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe" -or
          (Get-ItemProperty "HKCU:\Software\Google\Chrome\BLBeacon" -ErrorAction SilentlyContinue)
if ($chrome) { Write-Host "已检测到 Chrome。" -ForegroundColor Green }
else {
    Write-Host "建议安装 Google Chrome: https://www.google.com/chrome/" -ForegroundColor Gray
}
Write-Host ""

# 3. 虚拟环境与依赖
Write-Host "[3/4] 创建虚拟环境并安装依赖..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip -q
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "依赖安装失败，可尝试: pip install selenium beautifulsoup4" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 4. 运行
Write-Host "[4/4] 运行程序..." -ForegroundColor Yellow
Write-Host "无头模式可先: `$env:HEADLESS=1" -ForegroundColor Gray
Write-Host ""
python nize_kms.py
