# Windows 安装与运行说明（onlineshop / nize_kms）

## 一、环境要求

- **Windows** 10 或 11
- **Python** 3.8+（建议 3.10+）
- **Google Chrome**（脚本抓取数据用，Selenium 会自动匹配 ChromeDriver）

## 二、快速安装

### 方式 A：双击运行（推荐）

1. 进入项目目录 `onlineshop`
2. 双击 **`install_windows.bat`**
3. 若未装 Python，按提示先安装并勾选 “Add Python to PATH”，再重新双击运行

### 方式 B：PowerShell

```powershell
cd onlineshop
.\install_windows.ps1
```

若提示“无法加载，因为在此系统上禁止运行脚本”，先执行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 方式 C：命令行（CMD）

```cmd
cd onlineshop
install_windows.bat
```

脚本会：检查 Python/Chrome → 创建虚拟环境 `.venv` → 安装依赖 → 运行 `nize_kms.py`。

## 三、手动安装步骤

### 1. 安装 Python

- 打开 [Python 官网](https://www.python.org/downloads/)，下载 Windows 安装包。
- 安装时**务必勾选** “Add Python to PATH”。
- 或使用 winget：`winget install Python.Python.3.12`

### 2. 安装 Chrome（若未安装）

- 打开 [Chrome 官网](https://www.google.com/chrome/) 下载并安装。
- 脚本依赖 Chrome 进行页面抓取；Selenium 4 会自动管理 ChromeDriver，一般无需单独安装。

### 3. 创建虚拟环境并安装依赖

在 **命令提示符** 或 **PowerShell** 中：

```cmd
cd 你的路径\GetMall\onlineshop
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 运行程序

```cmd
python nize_kms.py
```

程序会按脚本内配置的 URL 与间隔定时抓取库存并保存为 JSON 文件。

## 四、无头模式（不弹出浏览器窗口）

在运行前设置环境变量再执行脚本：

**CMD：**

```cmd
set HEADLESS=1
python nize_kms.py
```

**PowerShell：**

```powershell
$env:HEADLESS=1
python nize_kms.py
```

## 五、常见问题

| 问题 | 处理 |
|------|------|
| “python 不是内部或外部命令” | 未将 Python 加入 PATH，重新安装并勾选 Add to PATH，或使用“ py ”命令：`py -m venv .venv` |
| Chrome/ChromeDriver 报错 | 确保已安装最新版 Chrome；若仍报错，可从 [ChromeDriver](https://chromedriver.chromium.org/downloads) 下载与 Chrome 版本一致的驱动并放到 PATH |
| 依赖安装失败（matplotlib/Pillow） | 脚本已不强制依赖 matplotlib，仅需：`pip install selenium beautifulsoup4`；若需绘图再单独安装 matplotlib |
| 用户数据目录 “already in use” | 脚本已做处理；若仍报错，可关闭其他 Chrome 窗口后重试，或稍等几秒再运行 |

## 六、依赖列表（requirements.txt）

- **selenium** >= 3.141.0  
- **beautifulsoup4** >= 4.12.0  
- **matplotlib** 可选（仅绘图时需要）

## 七、目录结构说明

- `nize_kms.py` — 主程序（抓取库存、保存 JSON）
- `install_windows.bat` — 一键安装并运行（CMD）
- `install_windows.ps1` — 一键安装并运行（PowerShell）
- `requirements.txt` — Python 依赖
- `.venv` — 虚拟环境目录（安装时自动创建）
