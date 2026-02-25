# 微店库存采集 (onlineshop)

定时采集微店商品库存，按链接分别保存 JSON，下架时间前后可加密集采集；支持配置、logs 归档与 html 展示。

## 使用前准备

1. **安装 Python 3.7+** 与 **Chrome 浏览器**
2. **复制配置**：`config.ini.example` → `config.ini`，在 `config.ini` 中填写真实商品链接与下架时间（可选）
3. **安装依赖**：`pip install -r requirements.txt`

## 运行

- Windows: 双击 `run.bat` 或 `python nize_kms.py`
- Linux: `python3 nize_kms.py`（无显示器可设 `HEADLESS=1`）

默认无头模式（后台运行、不显示窗口与任务栏）；需看到浏览器时设环境变量 `HEADLESS=0`。

## 提交到 GitHub

在项目目录下执行：

```bash
# 1. 在 GitHub 网页上新建仓库（如 yourname/onlineshop），不要勾选 “Add a README”

# 2. 添加远程并推送（把 YOUR_USERNAME/onlineshop 换成你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/onlineshop.git
git branch -M main
git push -u origin main
```

若使用 SSH：

```bash
git remote add origin git@github.com:YOUR_USERNAME/onlineshop.git
git push -u origin main
```
