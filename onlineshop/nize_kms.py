import os
import sys
import time
import tempfile
import glob
import shutil
import configparser
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json

# matplotlib 可选：未安装时仅无法绘图，抓取与保存 JSON 照常
try:
    import matplotlib.pyplot as plt
    if sys.platform == 'win32':
        plt.rcParams['font.sans-serif'] = ['SimHei']
    else:
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    HAS_MATPLOTLIB = True
except ImportError:
    plt = None
    HAS_MATPLOTLIB = False

# 假设这是你的函数，用来获取库存数据
# def fetch_stock_data():
#     # 这里应该是你调用 Selenium 的代码
#     # 现在我将返回一个示例数据
#     return {
#         "total_stock": 4999994,
#         "赵美延;韩国收货": 999998,
#         "MINNIE;韩国收货": 999999,
#         "田小娟;韩国收货": 999999,
#         "宋雨琦;韩国收货": 999999,
#         "叶舒华;韩国收货": 999999
#     }






def fetch_stock_data(url, headless=False):
    opts = Options()
    opts.add_argument('--no-first-run')
    opts.add_argument('--no-default-browser-check')
    # 不指定 --user-data-dir，避免部分环境下 "already in use"；若仍报错可试环境变量 SKIP_USER_DATA_DIR=0 改用临时目录
    chrome_tmp = None
    if os.environ.get('SKIP_USER_DATA_DIR', '1').strip() != '0':
        pass  # 不使用 user-data-dir
    else:
        chrome_tmp = os.path.join(tempfile.gettempdir(), 'chrome_selenium_%s_%s' % (os.getpid(), time.time()))
        os.makedirs(chrome_tmp, exist_ok=True)
        opts.add_argument('--user-data-dir=' + os.path.abspath(chrome_tmp))
    if headless:
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-gpu')
    # 后台运行：无头模式不显示窗口；Windows 下隐藏 chromedriver 控制台窗口，避免状态栏出现
    service = None
    if sys.platform == 'win32':
        try:
            import subprocess
            from selenium.webdriver.chrome.service import Service as ChromeService
            service = ChromeService()
            if hasattr(subprocess, 'CREATE_NO_WINDOW'):
                service.creationflags = subprocess.CREATE_NO_WINDOW
        except (TypeError, ImportError, AttributeError):
            pass
    driver = webdriver.Chrome(service=service, options=opts) if service else webdriver.Chrome(options=opts)

    # 访问目标网站
    driver.get(url)

    # 等待页面加载完成
    driver.implicitly_wait(10)

    # 使用 BeautifulSoup 解析页面源码
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 找到包含数据的 <script> 标签
    script_tag = soup.find('script', {'id': '__rocker-render-inject__'})
    stock_data = {}

    # 提取并解析 JSON 数据
    if script_tag:
        data_obj_str = script_tag.get('data-obj', '{}').replace('&quot;', '"')
        data_obj = json.loads(data_obj_str)
        
        # 提取总库存数
        total_stock = data_obj.get("result", {}).get("default_model", {}).get("item_info", {}).get("stock", "Stock not found")
        stock_data['总销量'] = total_stock
        
        # 提取SKU信息
        sku_info = data_obj.get("result", {}).get("default_model", {}).get("sku_properties", {}).get("sku", {})

        for sku_id, sku_details in sku_info.items():
            item_title = sku_details.get("title", "No title")
            item_stock = sku_details.get("stock", "No stock info")
            stock_data[item_title] = item_stock
    # 关闭浏览器
    driver.quit()
    time.sleep(1)  # 等待进程与文件锁释放，避免下次启动报 "already in use"
    if chrome_tmp and os.path.exists(chrome_tmp):
        try:
            import shutil
            shutil.rmtree(chrome_tmp, ignore_errors=True)
        except Exception:
            pass
    return stock_data



# 将根目录下的 JSON 复制到 logs 并删除，根目录只保留本轮即将写入的最新文件
LOGS_DIR = "logs"
HTML_DIR = "html"


def ensure_logs_dir():
    os.makedirs(LOGS_DIR, exist_ok=True)


def archive_root_jsons_to_logs():
    """把当前目录下所有 .json 复制到 logs/，并从根目录删除。"""
    ensure_logs_dir()
    for path in glob.glob("*.json"):
        dst = os.path.join(LOGS_DIR, path)
        try:
            shutil.copy2(path, dst)
            os.remove(path)
        except Exception:
            pass


def write_latest_to_html(current_time, stock_histories, off_shelf_times=None):
    """将最新一组数据写入 html/data.json，供网站展示。off_shelf_times 与 links 一一对应。"""
    os.makedirs(HTML_DIR, exist_ok=True)
    if off_shelf_times is None:
        off_shelf_times = [""] * len(stock_histories)
    payload = {
        "updated": current_time,
        "links": [
            {
                "link": i,
                "下架时间": off_shelf_times[i] if i < len(off_shelf_times) else "",
                "data": stock_histories[i][current_time],
            }
            for i in range(len(stock_histories))
        ],
    }
    path = os.path.join(HTML_DIR, "data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


# 下架时间前后使用密集采集：前后各 10 分钟、每 30 秒执行一次
OFF_SHELF_WINDOW_MINUTES = 10
OFF_SHELF_INTERVAL_SECONDS = 30


def _parse_off_shelf_time(s):
    """解析下架时间字符串为 datetime，失败返回 None。支持 2026-03-01 23:59:59 / 03-01 23:59:59 等。"""
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m-%d %H:%M:%S", "%m-%d %H:%M"):
        try:
            dt = datetime.strptime(s, fmt)
            if dt.year == 1900 and "%Y" not in fmt:
                dt = dt.replace(year=datetime.now().year)
            return dt
        except ValueError:
            continue
    return None


def _sleep_interval_around_off_shelf(interval, off_shelf_times):
    """若当前时间在任一链接的「下架前10分钟～下架后10分钟」内，返回 30 秒，否则返回 interval。"""
    if not off_shelf_times:
        return interval
    now = datetime.now()
    window = timedelta(minutes=OFF_SHELF_WINDOW_MINUTES)
    for s in off_shelf_times:
        dt = _parse_off_shelf_time(s)
        if dt is None:
            continue
        if now >= dt - window and now <= dt + window:
            return OFF_SHELF_INTERVAL_SECONDS
    return interval


# 定义查询函数：每个 URL 单独一份历史，输出到不同文件（*_link0.json, *_link1.json, ...）
def query_stocks(urls, interval, count, stock_histories, headless=False, off_shelf_times=None):
    # stock_histories: 列表，与 urls 一一对应，每项为该链接的 {时间: stock_data}
    if len(stock_histories) != len(urls):
        stock_histories = [dict(h) for h in stock_histories]
        while len(stock_histories) < len(urls):
            stock_histories.append({})
        stock_histories = stock_histories[: len(urls)]
    for idx in range(count):
        # 每轮写入前：将上期根目录的 JSON 归档到 logs，根目录只保留本轮要写的新文件
        archive_root_jsons_to_logs()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_suffix = current_time.replace(' ', '_').replace(':', '_')
        base_name = str(idx) + '-' + time_suffix

        for url_i, url in enumerate(urls):
            current_stocks = fetch_stock_data(url, headless=headless)
            stock_histories[url_i][current_time] = add_remainder_to_stock(current_stocks)
            # 每个链接单独一个文件
            filename = base_name + '_link' + str(url_i) + '.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stock_histories[url_i], f, indent=4, ensure_ascii=False)

        # 更新 html/data.json，供网站显示最新一组 key:value
        write_latest_to_html(current_time, stock_histories, off_shelf_times=off_shelf_times)

        # 下架前/后各 10 分钟内改为每半分钟执行一次，否则按 interval
        sleep_sec = _sleep_interval_around_off_shelf(interval, off_shelf_times)
        time.sleep(sleep_sec)



# 绘图并保存图像的函数（需要安装 matplotlib）
def save_stock_changes(stock_history, filename):
    if not HAS_MATPLOTLIB:
        raise RuntimeError('绘图需要安装 matplotlib，请运行: pip3 install matplotlib 或 sudo apt install python3-matplotlib')
    # 创建一个图和多个子图
    fig, axs = plt.subplots(len(stock_history[next(iter(stock_history))]), 1, figsize=(10, 20))
    fig.tight_layout(pad=3.0)
    
    for idx, sku in enumerate(stock_history[next(iter(stock_history))].keys()):
        times = list(stock_history.keys())
        values = [stocks[sku] for time, stocks in stock_history.items()]
        
        axs[idx].plot(times, values, marker='o', label=f'库存变化 {sku}')
        axs[idx].set_title(f'库存变化 {sku}')
        axs[idx].set_xlabel('时间')
        axs[idx].set_ylabel('库存数量')
        axs[idx].legend()
        axs[idx].tick_params(axis='x', rotation=45)
        for (a, b) in zip(times, values):
            axs[idx].text(a, b, str(b), horizontalalignment='center', verticalalignment='bottom')

    # 保存图像到文件
    num_queries = len(stock_history)
    #filename = f'stock_changes_{num_queries}_queries.png'
    plt.savefig(filename, format='png', dpi=300)
    plt.close()  # 关闭图像以释放内存

# 满量基准数：各 SKU 距满差 = 999999 - 数量；总销量_距满差 = 各分销量距满差之和
TARGET_MAX = 999999


def add_remainder_to_stock(stock_data):
    """为每个数值型数量增加「距满差」：各 SKU 用 999999 算距满差；总销量_距满差 = 各分销量距满差之和。"""
    result = dict(stock_data)
    sum_sku_remainder = 0
    for key, value in list(stock_data.items()):
        if not isinstance(value, (int, float)):
            continue
        if key == "总销量":
            continue
        remainder = TARGET_MAX - int(value)
        result[f"{key}_距满差"] = remainder
        sum_sku_remainder += remainder
    if "总销量" in stock_data and isinstance(stock_data["总销量"], (int, float)):
        result["总销量_距满差"] = sum_sku_remainder
    return result


# 从配置文件加载 URL 及每项配置（含下架时间）。使用 .ini 避免被归档到 logs 的 *.json 误移
CONFIG_PATH = "config.ini"


def load_url_config(path=CONFIG_PATH):
    """加载 config.ini，返回 (urls, off_shelf_times)。若文件不存在或为空则返回 ([], [])。"""
    if not os.path.isfile(path):
        return [], []
    try:
        parser = configparser.ConfigParser()
        parser.read(path, encoding="utf-8")
    except (configparser.Error, OSError):
        return [], []
    urls = []
    off_shelf_times = []
    # 按 link0, link1, ... 顺序读取
    i = 0
    while True:
        section = "link%d" % i
        if not parser.has_section(section):
            break
        url = parser.get(section, "url", fallback="").strip()
        if url:
            urls.append(url)
            off_shelf_times.append(parser.get(section, "下架时间", fallback="").strip() or "")
        i += 1
    return urls, off_shelf_times


urls, off_shelf_times = load_url_config()
if not urls:
    print("未找到有效 URL，请检查 config.ini 是否存在且包含 [link0] 等节的 url 项。")
    sys.exit(1)




# 用于保存数据的字典（每个链接一份）
# 运行查询函数，总共查询几次可以自己设置
# 默认无头模式：浏览器在后台运行、不显示窗口与任务栏。需显示窗口时设 HEADLESS=0
headless = os.environ.get('HEADLESS', '1').strip().lower() in ('1', 'true', 'yes')
# 按链接顺序加载历史，多个文件用英文逗号隔开，如 "link0.json,link1.json"
history_file = ""
history_files = [f.strip() for f in history_file.split(",") if f.strip()]
stock_histories = []
for i in range(len(urls)):
    if i < len(history_files):
        with open(history_files[i], 'r', encoding='utf-8') as f:
            stock_histories.append(json.load(f))
    else:
        stock_histories.append({})
if not stock_histories:
    stock_histories = [{} for _ in range(len(urls))]
# 建立 logs、html 目录，将根目录下过往的 json 全部复制到 logs 并删除，之后每轮由 query_stocks 内再归档
ensure_logs_dir()
os.makedirs(HTML_DIR, exist_ok=True)
archive_root_jsons_to_logs()
query_stocks(urls, 1800, 300, stock_histories, headless=headless, off_shelf_times=off_shelf_times)  # 1800 秒 = 30 分钟，300 = 查询次数
