from __future__ import annotations

import csv
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BILIBILI_HOME = "https://www.bilibili.com"


@dataclass
class CrawlConfig:
    mids: List[str]
    max_pages: int
    headless: bool
    timeout_sec: int
    sleep_sec: float
    output_dir: Path
    cookie_header: str = ""


def _parse_cookie_header(raw: str) -> List[Dict[str, str]]:
    cookies: List[Dict[str, str]] = []
    for part in raw.split(";"):
        segment = part.strip()
        if not segment or "=" not in segment:
            continue
        key, val = segment.split("=", 1)
        key = key.strip()
        val = val.strip()
        if key:
            cookies.append({"name": key, "value": val})
    return cookies


def read_cookie_header(cookie_file: Optional[Path] = None) -> str:
    env_cookie = os.environ.get("BILI_COOKIE", "").strip()
    if env_cookie:
        return env_cookie

    if not cookie_file:
        return ""

    if not cookie_file.exists():
        return ""

    text = cookie_file.read_text(encoding="utf-8").strip()
    if not text:
        return ""

    # Accept plain cookie string or JSON: {"cookie": "..."}
    if text.startswith("{"):
        try:
            data = json.loads(text)
            value = str(data.get("cookie", "")).strip()
            return value
        except json.JSONDecodeError:
            return ""
    return text


def _build_driver(headless: bool, timeout_sec: int) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1400,1800")
    options.add_argument("--lang=zh-CN")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(timeout_sec)
    return driver


def _apply_cookie_if_available(driver: webdriver.Chrome, cookie_header: str, sleep_sec: float) -> None:
    if not cookie_header:
        return

    driver.get(BILIBILI_HOME)
    time.sleep(sleep_sec)
    cookies = _parse_cookie_header(cookie_header)
    for cookie in cookies:
        try:
            driver.add_cookie(
                {
                    "name": cookie["name"],
                    "value": cookie["value"],
                    "domain": ".bilibili.com",
                    "path": "/",
                }
            )
        except Exception:
            # Ignore invalid/unsupported cookie fields and continue.
            continue


def _extract_cards(driver: webdriver.Chrome) -> List:
    selectors = [
        ".video-list .bili-video-card",
        ".video-list__wrap .bili-video-card",
        ".small-item",
    ]
    for selector in selectors:
        cards = driver.find_elements(By.CSS_SELECTOR, selector)
        if cards:
            return cards
    return []


def _first_text(card, selectors: List[str]) -> str:
    for selector in selectors:
        nodes = card.find_elements(By.CSS_SELECTOR, selector)
        for node in nodes:
            text = (node.text or "").strip()
            if text:
                return text
    return ""


def _first_href(card, selectors: List[str]) -> str:
    for selector in selectors:
        nodes = card.find_elements(By.CSS_SELECTOR, selector)
        for node in nodes:
            href = (node.get_attribute("href") or "").strip()
            if href:
                return href.split("?", 1)[0]
    return ""


def _detect_up_name(driver: webdriver.Chrome) -> str:
    selectors = [
        ".h .h-name",
        ".up-info-container .nickname",
        ".up-name",
    ]
    for selector in selectors:
        nodes = driver.find_elements(By.CSS_SELECTOR, selector)
        if nodes:
            name = (nodes[0].text or "").strip()
            if name:
                return name
    return ""


def _extract_from_initial_state(driver: webdriver.Chrome, mid: str, up_name: str, page: int) -> List[Dict[str, str]]:
    """Fallback: parse window.__INITIAL_STATE__ JSON when DOM selectors fail."""
    html = driver.page_source or ""
    m = re.search(r"__INITIAL_STATE__\s*=\s*(\{.*?\})\s*;\s*\(function", html, re.S)
    if not m:
        return []

    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []

    # Common path for space video list pages
    vlist = (
        data.get("arc", {})
        .get("video", {})
        .get("vlist", [])
    )
    if not isinstance(vlist, list) or not vlist:
        return []

    rows: List[Dict[str, str]] = []
    crawl_time = datetime.now().isoformat(timespec="seconds")
    for item in vlist:
        bvid = str(item.get("bvid", "")).strip()
        aid = str(item.get("aid", "")).strip()
        video_url = ""
        if bvid:
            video_url = f"https://www.bilibili.com/video/{bvid}"
        elif aid:
            video_url = f"https://www.bilibili.com/video/av{aid}"

        created = item.get("created")
        publish_time = ""
        if isinstance(created, (int, float)) and created > 0:
            publish_time = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M:%S")

        play = item.get("play")
        play_count = str(play) if play is not None else ""

        rows.append(
            {
                "up_mid": mid,
                "up_name": up_name or str(data.get("card", {}).get("name", "")).strip(),
                "page": str(page),
                "title": str(item.get("title", "")).strip(),
                "video_url": video_url,
                "publish_time": publish_time,
                "play_count": play_count,
                "crawl_time": crawl_time,
            }
        )

    return rows


def _collect_from_page(driver: webdriver.Chrome, mid: str, up_name: str, page: int) -> List[Dict[str, str]]:
    cards = _extract_cards(driver)
    rows: List[Dict[str, str]] = []
    crawl_time = datetime.now().isoformat(timespec="seconds")

    for card in cards:
        title = _first_text(
            card,
            [
                "a.bili-video-card__info--tit",
                "a.title",
                ".bili-video-card__info--tit",
            ],
        )
        video_url = _first_href(card, ["a.bili-video-card__wrap", "a.cover", "a"])
        publish_time = _first_text(
            card,
            [
                ".bili-video-card__info--date",
                ".meta .time",
                ".time",
            ],
        )
        play_count = _first_text(
            card,
            [
                ".bili-video-card__stats--item",
                ".meta .play",
                ".play",
            ],
        )

        if not title and not video_url:
            continue

        rows.append(
            {
                "up_mid": mid,
                "up_name": up_name,
                "page": str(page),
                "title": title,
                "video_url": video_url,
                "publish_time": publish_time,
                "play_count": play_count,
                "crawl_time": crawl_time,
            }
        )

    if rows:
        return rows

    return _extract_from_initial_state(driver, mid=mid, up_name=up_name, page=page)


def crawl_up_videos(config: CrawlConfig) -> List[Dict[str, str]]:
    all_rows: List[Dict[str, str]] = []
    driver = _build_driver(headless=config.headless, timeout_sec=config.timeout_sec)

    try:
        _apply_cookie_if_available(driver, config.cookie_header, config.sleep_sec)

        for mid in config.mids:
            up_name = ""
            for page in range(1, config.max_pages + 1):
                # 优先使用 upload/video（与原项目一致），失败再回退 video 路径。
                candidate_urls = [
                    f"https://space.bilibili.com/{mid}/upload/video?tid=0&page={page}&keyword=&order=pubdate",
                    f"https://space.bilibili.com/{mid}/video?tid=0&page={page}&keyword=&order=pubdate",
                ]

                last_rows: List[Dict[str, str]] = []
                for url in candidate_urls:
                    driver.get(url)

                    try:
                        WebDriverWait(driver, config.timeout_sec).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                        )
                    except TimeoutException:
                        continue

                    time.sleep(config.sleep_sec)

                    if not up_name:
                        up_name = _detect_up_name(driver)

                    rows = _collect_from_page(driver, mid=mid, up_name=up_name, page=page)
                    if rows:
                        all_rows.extend(rows)
                        last_rows = rows
                        break

                if not last_rows:
                    break

    finally:
        driver.quit()

    return all_rows


def write_csv(rows: List[Dict[str, str]], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"bilibili_videos_{timestamp}.csv"

    fieldnames = [
        "up_mid",
        "up_name",
        "page",
        "title",
        "video_url",
        "publish_time",
        "play_count",
        "crawl_time",
    ]

    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path
