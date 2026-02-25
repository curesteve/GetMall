#!/bin/bash
# GetMall onlineshop - Linux 安装与运行脚本
# 适用于 Ubuntu/Debian（其他发行版请根据包管理器调整）

set -e
cd "$(dirname "$0")"

echo "=== 1. 安装系统依赖（含 Chromium 浏览器，脚本抓数据必需）==="
# Chromium/Chrome 与 ChromeDriver（Selenium 抓取用）+ 中文字体（matplotlib 绘图用）
if command -v apt-get &>/dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
    # 安装 Chromium 浏览器（脚本获取数据必需）
    if ! command -v google-chrome &>/dev/null && ! command -v chromium &>/dev/null && ! command -v chromium-browser &>/dev/null; then
        echo "正在安装 Chromium 浏览器..."
        sudo apt-get install -y chromium-browser 2>/dev/null || sudo apt-get install -y chromium || true
    fi
    # ChromeDriver（与 Chromium 配套，Selenium 驱动浏览器用）
    sudo apt-get install -y chromium-chromedriver 2>/dev/null || true
    # 中文字体（避免 matplotlib 中文乱码）
    sudo apt-get install -y fonts-wqy-microhei || true
elif command -v dnf &>/dev/null; then
    sudo dnf install -y python3 python3-pip
    sudo dnf install -y chromium chromedriver || true
    sudo dnf install -y wqy-microhei-fonts || true
elif command -v yum &>/dev/null; then
    sudo yum install -y python3 python3-pip
    sudo yum install -y chromium chromedriver || true
fi

echo "=== 2. 创建虚拟环境并安装 Python 依赖 ==="
python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo "=== 3. 运行程序 ==="
echo "执行: python nize_kms.py"
echo "（如需无头模式，请: HEADLESS=1 python3 nize_kms.py）"
python3 nize_kms.py
