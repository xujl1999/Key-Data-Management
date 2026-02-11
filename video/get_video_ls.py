from pathlib import Path
import argparse
import json
import os
import random
import time
from typing import Dict, List, Optional

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.yaml"
DEFAULT_DEBUG_DIR = BASE_DIR / "debug"


def load_config() -> Dict:
    raw = CONFIG_PATH.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(raw)
    return json.loads(raw)


def random_between(span: List[float]) -> float:
    return random.uniform(span[0], span[1])


def human_scroll(driver: webdriver.Chrome, min_scrolls: int, max_scrolls: int) -> None:
    steps = random.randint(min_scrolls, max_scrolls)
    for _ in range(steps):
        scroll_px = random.randint(300, 1200)
        driver.execute_script(
            "window.scrollBy({ top: arguments[0], behavior: 'smooth' });", scroll_px
        )
        time.sleep(random_between([0.8, 1.6]))
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(random_between([0.5, 1.0]))


def parse_cookie_header(raw: str) -> List[Dict[str, str]]:
    cookies: List[Dict[str, str]] = []
    for part in raw.split(";"):
        seg = part.strip()
        if not seg or "=" not in seg:
            continue
        k, v = seg.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        cookies.append({"name": k, "value": v})
    return cookies


def apply_bili_cookies_if_any(driver: webdriver.Chrome) -> None:
    raw = (os.environ.get("BILI_COOKIE") or "").strip()
    if not raw:
        return
    try:
        cookies = parse_cookie_header(raw)
        if not cookies:
            return
        for ck in cookies:
            driver.add_cookie(
                {
                    "name": ck["name"],
                    "value": ck["value"],
                    "domain": ".bilibili.com",
                    "path": "/",
                }
            )
        driver.refresh()
        time.sleep(random_between([1.2, 2.2]))
    except Exception:
        # cookie 注入失败时不阻断主流程
        pass


def build_driver(browser_options: List[str], headless: bool) -> webdriver.Chrome:
    options = Options()
    for opt in browser_options:
        options.add_argument(opt)
    if headless:
        # 使用新版 headless 以减少兼容性问题
        options.add_argument("--headless=new")
    # ---- 关键：绕过系统代理直连 B站（避免海外出口触发风控） ----
    options.add_argument("--no-proxy-server")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.bilibili.com")
    time.sleep(random_between([1.5, 3.5]))
    apply_bili_cookies_if_any(driver)
    return driver


def normalize_authors(data) -> List[Dict]:
    authors: List[Dict] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                authors.append(item)
            elif isinstance(item, str):
                authors.append({"author_id": item})
        return authors

    if isinstance(data, dict):
        for category, items in data.items():
            if isinstance(category, str) and category.startswith("_"):
                continue
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    entry = dict(item)
                    entry.setdefault("category", category)
                    authors.append(entry)
                elif isinstance(item, str):
                    authors.append({"author_id": item, "category": category})
        return authors

    raise ValueError("Unsupported authors format")


def load_authors(authors_path: Path) -> List[Dict]:
    with authors_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return normalize_authors(data)


def detect_failure_reason(driver: webdriver.Chrome, source: str) -> str:
    title = (driver.title or "").strip()
    cur = driver.current_url
    if "passport.bilibili.com" in cur or "登录" in title:
        return "登录态不足或跳转登录"
    if "出错" in title:
        return "页面出错（可能风控/反爬/临时异常）"
    if "验证码" in source or "安全验证" in source:
        return "命中验证码/安全校验"
    if "访问受限" in source or "请求被拦截" in source:
        return "可能被反爬拦截"
    if "/upload/video" not in cur:
        return f"页面跳转异常: {cur}"
    return "选择器失效或列表异步未完成"


def append_failure_log(debug_dir: Path, payload: Dict) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    log_path = debug_dir / "video_collect_failures.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def wait_video_cards(driver: webdriver.Chrome, timeout: int = 12):
    selectors = [
        ".video-list .bili-video-card",
        "div.bili-video-card",
        ".bili-video-card",
    ]
    wait = WebDriverWait(driver, timeout)
    for sel in selectors:
        try:
            return wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, sel) or None)
        except Exception:
            continue
    return []


def first_text(card, selectors: List[str]) -> str:
    for sel in selectors:
        els = card.find_elements(By.CSS_SELECTOR, sel)
        if els:
            t = (els[0].text or "").strip()
            if t:
                return t
    return ""


def first_href(card, selectors: List[str]) -> str:
    for sel in selectors:
        els = card.find_elements(By.CSS_SELECTOR, sel)
        if els:
            href = (els[0].get_attribute("href") or "").strip()
            if href:
                return href.split("?", 1)[0]
    return ""


def collect_from_cards(
    driver: webdriver.Chrome,
    author: Dict,
    cards,
    max_videos: int,
) -> List[Dict]:
    category = author.get("category", "")
    author_name = ""
    author_name_selectors = [
        "#app .upinfo-detail .nickname",
        "#app .up-name",
        ".h-name",
    ]
    for sel in author_name_selectors:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        if els:
            author_name = (els[0].text or "").strip()
            if author_name:
                break

    rows: List[Dict] = []
    for rank, card in enumerate(cards[:max_videos], start=1):
        url = first_href(card, [
            ".bili-video-card__cover a",
            "a[href*='/video/']",
        ])
        title = first_text(card, [
            ".bili-video-card__title a",
            ".bili-video-card__title",
            "a[title]",
        ])
        publish_date = first_text(card, [
            ".bili-video-card__subtitle span",
            ".bili-video-card__stats--left",
            ".bili-video-card__subtitle",
        ])
        if not title and not url:
            continue
        rows.append(
            {
                "category": category,
                "author": author_name or author.get("author_name", ""),
                "rank": rank,
                "publish_date": publish_date,
                "title": title,
                "url": url,
            }
        )
    return rows


def extract_initial_state(source: str) -> Optional[Dict]:
    markers = [
        "window.__INITIAL_STATE__=",
        "window.__INITIAL_STATE__ =",
    ]
    for marker in markers:
        idx = source.find(marker)
        if idx == -1:
            continue
        start = source.find("{", idx + len(marker))
        if start == -1:
            continue
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(source)):
            ch = source[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        blob = source[start : i + 1]
                        try:
                            return json.loads(blob)
                        except Exception:
                            return None
        return None
    return None


def find_video_items(state: Dict) -> List[Dict]:
    candidates: List[List[Dict]] = []

    def visit(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                visit(v)
        elif isinstance(obj, list):
            if obj and all(isinstance(it, dict) for it in obj):
                sample = obj[0]
                if "title" in sample and ("bvid" in sample or "aid" in sample):
                    candidates.append(obj)
            for it in obj:
                visit(it)

    visit(state)
    if not candidates:
        return []
    candidates.sort(key=len, reverse=True)
    return candidates[0]


def author_name_from_state(state: Dict) -> str:
    for path in [
        ("userInfo", "name"),
        ("userInfo", "uname"),
        ("userInfo", "username"),
        ("space", "name"),
        ("upinfo", "name"),
        ("upinfo", "uname"),
    ]:
        cur = state
        ok = True
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                ok = False
                break
            cur = cur[key]
        if ok and isinstance(cur, str) and cur.strip():
            return cur.strip()
    return ""


def collect_from_state(state: Dict, author: Dict, max_videos: int) -> List[Dict]:
    items = find_video_items(state)
    if not items:
        return []
    author_name = author_name_from_state(state) or author.get("author_name", "")
    rows: List[Dict] = []
    for rank, item in enumerate(items[:max_videos], start=1):
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip()
        bvid = (item.get("bvid") or "").strip()
        aid = item.get("aid")
        url = ""
        if bvid:
            url = f"https://www.bilibili.com/video/{bvid}"
        elif isinstance(aid, (int, str)) and str(aid).strip():
            url = f"https://www.bilibili.com/video/av{aid}"
        publish_date = ""
        ts = item.get("created") or item.get("pubdate")
        if isinstance(ts, (int, float)):
            publish_date = time.strftime("%Y-%m-%d", time.localtime(ts))
        rows.append(
            {
                "category": author.get("category", ""),
                "author": author_name,
                "rank": rank,
                "publish_date": publish_date,
                "title": title,
                "url": url,
            }
        )
    return [r for r in rows if r["title"] or r["url"]]


def collect_for_author(
    driver: webdriver.Chrome,
    author: Dict,
    sleep_after_load: List[float],
    scroll_min: int,
    scroll_max: int,
    max_videos: int,
    debug_dir: Path = DEFAULT_DEBUG_DIR,
) -> List[Dict]:
    author_id = author["author_id"]

    driver.get(f"https://space.bilibili.com/{author_id}/upload/video")
    time.sleep(random_between(sleep_after_load))
    human_scroll(driver, scroll_min, scroll_max)

    # 原有选择器逻辑：保留
    collected: List[Dict] = []
    for rank in range(1, max_videos + 1):
        try:
            base = f"#app > main > div.space-upload > div.upload-content > div > div.video-body > div > div:nth-child({rank}) > div > div > div > div > div.bili-video-card"
            url = (
                driver.find_element(By.CSS_SELECTOR, f"{base}__cover > a")
                .get_attribute("href")
                .split("?", 1)[0]
            )
            title = driver.find_element(
                By.CSS_SELECTOR, f"{base}__details > div.bili-video-card__title > a"
            ).text
            publish_date = driver.find_element(
                By.CSS_SELECTOR, f"{base}__details > div.bili-video-card__subtitle > span"
            ).text
            author_name = driver.find_element(
                By.CSS_SELECTOR,
                "#app > div.header.space-header > div.upinfo.header-upinfo > div.upinfo__main > div.upinfo-detail > div.upinfo-detail__top > div.nickname",
            ).text
        except Exception:
            break

        collected.append(
            {
                "category": author.get("category", ""),
                "author": author_name,
                "rank": rank,
                "publish_date": publish_date,
                "title": title,
                "url": url,
            }
        )

    if collected:
        return collected

    # 兜底逻辑：多选择器 + 等待
    cards = wait_video_cards(driver)
    fallback_rows = collect_from_cards(driver, author, cards, max_videos=max_videos)
    if fallback_rows:
        return fallback_rows

    # 兜底逻辑：从页面内嵌 JSON 解析
    state = extract_initial_state(driver.page_source)
    if isinstance(state, dict):
        json_rows = collect_from_state(state, author, max_videos=max_videos)
        if json_rows:
            return json_rows

    src = driver.page_source
    append_failure_log(
        debug_dir,
        {
            "ts": int(time.time()),
            "author_id": author_id,
            "author_name": author.get("author_name", ""),
            "url": driver.current_url,
            "title": driver.title,
            "reason": detect_failure_reason(driver, src),
        },
    )
    return []


def write_outputs(rows: List[Dict], outputs: List[str]) -> None:
    df = pd.DataFrame(rows)
    for out in outputs:
        target = (BASE_DIR / out).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(target, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="采集 B 站 UP 主视频列表")
    parser.add_argument("--smoke-author-id", help="仅采集单个 author_id，用于冒烟验证")
    parser.add_argument("--smoke-limit", type=int, default=1, help="冒烟时最多抓取条数")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    authors_path = BASE_DIR / config["authors_file"]
    authors = load_authors(authors_path)

    if args.smoke_author_id:
        one: Optional[Dict] = next(
            (a for a in authors if str(a.get("author_id")) == str(args.smoke_author_id)),
            None,
        )
        if not one:
            one = {"author_id": str(args.smoke_author_id), "category": "smoke"}
        authors = [one]

    driver = build_driver(
        config.get("chrome_options", config.get("edge_options", [])),
        headless=config.get("headless", False),
    )

    rows: List[Dict] = []
    try:
        for author in tqdm(authors):
            rows.extend(
                collect_for_author(
                    driver,
                    author,
                    sleep_after_load=config["sleep_after_load_seconds"],
                    scroll_min=config["scroll_steps"]["min"],
                    scroll_max=config["scroll_steps"]["max"],
                    max_videos=args.smoke_limit if args.smoke_author_id else config["max_videos_per_author"],
                )
            )
    finally:
        driver.quit()

    write_outputs(rows, config["outputs"])
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
