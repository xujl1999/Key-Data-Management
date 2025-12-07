from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # 当前py文件所在目录


from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from tqdm import tqdm
import json
import time
import random

COOKIE_FILE = "bili_cookies.json"


with open(COOKIE_FILE, "r", encoding="utf-8") as f:
    cookies = json.load(f)


options = Options()
options.add_argument("--edge-skip-compat-layer-relaunch")
driver = webdriver.Edge(options=options)

driver.get("https://www.bilibili.com")

for c in cookies:
    dom = c.get("domain", "")
    # 只处理和 bilibili 有关的 cookie
    if "bilibili.com" not in dom:
        continue

    cookie = {
        "name": c["name"],
        "value": c["value"],
        "domain": ".bilibili.com",
        "path": "/",
    }

    driver.add_cookie(cookie)

driver.refresh()  # 刷新后看是否已经是登录态

# time.sleep(2)
time.sleep(random.uniform(1.5, 3.5))
# 存查到的信息
rows = []


def human_scroll(driver, min_scrolls=1, max_scrolls=3):
    steps = random.randint(min_scrolls, max_scrolls)
    for _ in range(steps):
        scroll_px = random.randint(300, 1200)
        driver.execute_script("window.scrollBy({ top: arguments[0], behavior: 'smooth' });", scroll_px)
        time.sleep(random.uniform(0.8, 1.6))
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(random.uniform(0.5, 1.0))


with open("bilibili_authors.json", "r", encoding="utf-8") as f:
    author_config = json.load(f)

for i in tqdm(range(len(author_config))):
    category = author_config[i]['category']
    author_id = author_config[i]['author_id']
    author_name = author_config[i]['author_name']
    # 进入个人主页
    driver.get(f"https://space.bilibili.com/{author_id}/upload/video")
    
    time.sleep(random.uniform(5.5, 10.5))
    human_scroll(driver)
    # 每个人保存最新的10个视频
    for n in range(10): 
        rank=n+1
        url = driver.find_element(By.CSS_SELECTOR, f"#app > main > div.space-upload > div.upload-content > div > div.video-body > div > div:nth-child({rank}) > div > div > div > div > div.bili-video-card__cover > a").get_attribute("href").split("?", 1)[0]
        title = driver.find_element(By.CSS_SELECTOR, f"#app > main > div.space-upload > div.upload-content > div > div.video-body > div > div:nth-child({rank}) > div > div > div > div > div.bili-video-card__details > div.bili-video-card__title > a").text
        publish_date = driver.find_element(By.CSS_SELECTOR, f"#app > main > div.space-upload > div.upload-content > div > div.video-body > div > div:nth-child({rank}) > div > div > div > div > div.bili-video-card__details > div.bili-video-card__subtitle > span").text
        author = driver.find_element(By.CSS_SELECTOR, f"#app > div.header.space-header > div.upinfo.header-upinfo > div.upinfo__main > div.upinfo-detail > div.upinfo-detail__top > div.nickname").text
        rows.append({
            "category": category,
            "author": author,
            "rank": rank,
            "publish_date": publish_date,
            "title": title,
            "url": url
        })

df = pd.DataFrame(rows)
df.to_csv('video_ls.csv')
df.to_csv('../web/video_ls.csv')

# # 筛选优质博主 # 改为前端逻辑
# df = pd.read_csv('video_ls.csv')
# condition_author = df['category'].isin(['超优质', '历史区', '创意区'])
# condition_rank = df['rank'] <= 1
# exhibit_col = ['author', 'title', 'url']

# df[condition_author & condition_rank][exhibit_col].to_csv('out_video_ls.csv')