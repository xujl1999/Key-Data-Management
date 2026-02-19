"""抓取 YouTube 频道最新视频列表（通过 RSS feed）。

用法：
    python get_youtube_ls.py                           # 全量抓取
    python get_youtube_ls.py --smoke-channel-id UCXXX  # 冒烟测试
    python get_youtube_ls.py --days 7                  # 仅保留近 7 天
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import ssl
import urllib.request

import feedparser
import pandas as pd

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.yaml"

RSS_URL_TEMPLATE = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
_SSL_CTX = ssl.create_default_context()
_HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


# ─── Config ────────────────────────────────────────────────────

def load_config() -> Dict:
    raw = CONFIG_PATH.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(raw)
    return json.loads(raw)


# ─── Channels ──────────────────────────────────────────────────

def load_channels(channels_path: Path) -> List[Dict]:
    with channels_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    channels: List[Dict] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                channels.append(item)
            elif isinstance(item, str):
                channels.append({"channel_id": item})
        return channels

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
                    channels.append(entry)
                elif isinstance(item, str):
                    channels.append({"channel_id": item, "category": category})
        return channels

    raise ValueError("Unsupported channels format")


# ─── RSS Fetching ──────────────────────────────────────────────

def fetch_channel_videos(
    channel: Dict,
    max_videos: int = 10,
    days_filter: Optional[int] = None,
) -> List[Dict]:
    """Fetch videos from a YouTube channel's RSS feed."""
    channel_id = channel["channel_id"]
    category = channel.get("category", "")
    channel_name = channel.get("channel_name", "")

    url = RSS_URL_TEMPLATE.format(channel_id=channel_id)

    try:
        req = urllib.request.Request(url, headers=_HTTP_HEADERS)
        resp = urllib.request.urlopen(req, timeout=15, context=_SSL_CTX)
        raw_xml = resp.read()
        feed = feedparser.parse(raw_xml)
    except Exception as e:
        print(f"  ⚠ Failed to fetch RSS for {channel_name or channel_id}: {e}")
        return []

    # Use channel title from feed if not in config
    if not channel_name and feed.feed.get("title"):
        channel_name = feed.feed.title

    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=days_filter)) if days_filter else None

    rows: List[Dict] = []
    for rank, entry in enumerate(feed.entries[:max_videos], start=1):
        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()

        # Parse published date
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if published:
            dt = datetime(*published[:6], tzinfo=timezone.utc)
            publish_date = dt.strftime("%Y-%m-%d")
        else:
            dt = None
            publish_date = ""

        # Apply days filter
        if cutoff and dt and dt < cutoff:
            continue

        # Extract video ID from link
        video_id = ""
        if "watch?v=" in link:
            video_id = link.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in link:
            video_id = link.split("youtu.be/")[-1].split("?")[0]

        if not title and not link:
            continue

        rows.append({
            "category": category,
            "channel": channel_name,
            "rank": rank,
            "publish_date": publish_date,
            "title": title,
            "url": link,
            "video_id": video_id,
            "summary": "",
        })

    return rows


# ─── Output ────────────────────────────────────────────────────

def write_outputs(rows: List[Dict], outputs: List[str]) -> None:
    df = pd.DataFrame(rows)
    for out in outputs:
        target = (BASE_DIR / out).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)

        # Incremental: preserve existing summary values
        if target.exists() and "summary" in df.columns:
            try:
                old = pd.read_csv(target, dtype=str).fillna("")
                if "video_id" in old.columns and "summary" in old.columns:
                    summary_map = dict(
                        zip(old["video_id"], old["summary"])
                    )
                    kept = 0
                    for i, row in df.iterrows():
                        vid = row.get("video_id", "")
                        old_summary = summary_map.get(vid, "")
                        cur_summary = str(row.get("summary", "")).strip()
                        if not cur_summary and old_summary:
                            df.at[i, "summary"] = old_summary
                            kept += 1
                    if kept:
                        print(f"  ℹ Preserved {kept} existing summaries")
            except Exception as e:
                print(f"  ⚠ Could not merge old summaries: {e}")

        df.to_csv(target, index=False)
        print(f"  ✓ Wrote {len(df)} rows → {target}")


# ─── CLI ───────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取 YouTube 频道最新视频列表")
    parser.add_argument("--smoke-channel-id", help="仅抓取单个 channel_id，用于冒烟验证")
    parser.add_argument("--smoke-limit", type=int, default=3, help="冒烟时最多抓取条数（默认 3）")
    parser.add_argument("--days", type=int, default=None, help="仅保留最近 N 天的视频")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()

    channels_path = BASE_DIR / config["channels_file"]
    channels = load_channels(channels_path)

    max_videos = config.get("max_videos_per_channel", 10)

    if args.smoke_channel_id:
        one: Optional[Dict] = next(
            (c for c in channels if str(c.get("channel_id")) == str(args.smoke_channel_id)),
            None,
        )
        if not one:
            one = {"channel_id": str(args.smoke_channel_id), "category": "smoke"}
        channels = [one]
        max_videos = args.smoke_limit

    print(f"Fetching videos from {len(channels)} channel(s)...")
    all_rows: List[Dict] = []
    for ch in channels:
        name = ch.get("channel_name") or ch["channel_id"]
        print(f"  → {name}")
        rows = fetch_channel_videos(
            ch,
            max_videos=max_videos,
            days_filter=args.days,
        )
        all_rows.extend(rows)
        # Small courtesy delay between requests
        if len(channels) > 1:
            time.sleep(0.5)

    write_outputs(all_rows, config["outputs"])
    print(f"Done. Total rows={len(all_rows)}")


if __name__ == "__main__":
    main()
