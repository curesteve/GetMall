import os
import sys
import time
import tempfile
from datetime import datetime
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
    driver = webdriver.Chrome(options=opts)

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



# 定义查询函数
def query_stocks(urls, interval, count, stock_history, headless=False):
    for idx in range(count):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        stock_data = {}

        # 处理每个 URL
        for url in urls:
            current_stocks = fetch_stock_data(url, headless=headless)
            for title, stock in current_stocks.items():
                if title in stock_data:
                    stock_data[title] += stock
                else:
                    stock_data[title] = stock
        # # 打印结果
        # for title, total_stock in stock_data.items():
        #     print(f"{title}: {total_stock}")


        # stock_data = fetch_stock_data()
        stock_history[current_time] = stock_data
        name = str(idx)+'-'+current_time.replace(' ','_').replace(':','_')
        # 生成图像
        #save_stock_changes(stock_history,name+'.png')
        # 保存当前数据
        with open(name+'.json', 'w',encoding='utf-8') as f:
            json.dump(stock_history, f, indent=4, ensure_ascii=False)
        # 等待一段时间，这里是5分钟,根据interval决定
        time.sleep(interval)



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

# URL 列表  在''里粘贴微店网址，多个网址用,隔开
urls = [
 'https://k.youshop10.com/AzkRRBXU?a=b&p=iphone&wfr=BuyercopyURL&share_relation=9c22c593e1d9a5e7_1470530718_1'
]








# 用于保存数据的字典
# 运行查询函数，总共查询几次可以自己设置
# 无头模式：Linux 无显示器时可设 HEADLESS=1，如 HEADLESS=1 python nize_kms.py
headless = os.environ.get('HEADLESS', '').strip().lower() in ('1', 'true', 'yes')
history_file = ""#如果有需要加载的就写文件名，没有就保持""
if history_file != "":#加载之前的数据
    with open(history_file, 'r',encoding='utf-8') as f:
        stock_history = json.load(f)
    query_stocks(urls, 1800, 300, stock_history, headless=headless)  # 60 seconds = 1 minutes，300 = 查询次数
else:
    stock_history = {}
    query_stocks(urls, 1800, 300, stock_history, headless=headless)  # 60 seconds = 5 minutes，300 = 查询次数

