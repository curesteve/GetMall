# Linux 安装与运行说明（onlineshop / nize_kms）

## 一、环境要求

- **Python** 3.8+
- **Chrome 或 Chromium** 及对应 **ChromeDriver**（Selenium 用）
- **中文字体**（可选，用于 matplotlib 绘图时显示中文）

## 二、快速安装（Ubuntu/Debian）

```bash
cd onlineshop
chmod +x install_linux.sh
./install_linux.sh
```

脚本会：安装系统依赖、创建虚拟环境、安装 Python 包并运行 `nize_kms.py`。

## 三、手动安装步骤

### 1. 安装 Python 与 pip

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Fedora/CentOS
sudo dnf install -y python3 python3-pip
```

### 2. 安装 Chrome/Chromium 与 ChromeDriver

**方式 A：Chromium（推荐，包管理器直接安装）**

```bash
# Ubuntu/Debian
sudo apt-get install -y chromium-browser
# ChromeDriver 可能与 Chromium 同包或需单独安装
sudo apt-get install -y chromium-chromedriver   # 若有此包

# Fedora
sudo dnf install -y chromium chromedriver
```

**方式 B：Google Chrome**

- 从 [Chrome 官网](https://www.google.com/chrome/) 下载并安装。
- ChromeDriver：从 [Chromedriver 下载页](https://chromedriver.chromium.org/downloads) 下载与 Chrome 版本匹配的驱动，解压后放到 `PATH` 或项目目录。

### 3. 安装中文字体（避免 matplotlib 中文乱码）

```bash
# Ubuntu/Debian
sudo apt-get install -y fonts-wqy-microhei

# Fedora
sudo dnf install -y wqy-microhei-fonts
```

### 4. 创建虚拟环境并安装依赖

```bash
cd onlineshop
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. 运行

```bash
python3 nize_kms.py
```

程序会按脚本内配置的 URL 与间隔定时抓取库存并保存为 JSON 文件。

## 四、无图形界面（无头模式）运行

若在无显示器的服务器上运行，需使用 Chrome 无头模式。在 `nize_kms.py` 中可将：

```python
driver = webdriver.Chrome()
```

改为：

```python
from selenium.webdriver.chrome.options import Options
opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=opts)
```

## 五、常见问题

| 问题 | 处理 |
|------|------|
| `Chrome not found` / ChromeDriver 报错 | 确认已安装 Chrome 或 Chromium，且 ChromeDriver 版本与浏览器一致、在 `PATH` 中 |
| matplotlib 中文为方框 | 安装 `fonts-wqy-microhei` 或 `Noto Sans CJK`，脚本已做 Linux 字体回退 |
| 权限错误 | 使用 `python3 -m venv .venv` 与 `source .venv/bin/activate` 在用户目录下运行，避免写系统目录 |

## 六、依赖列表（requirements.txt）

- selenium >= 4.6.0  
- beautifulsoup4 >= 4.12.0  
- matplotlib >= 3.7.0  
