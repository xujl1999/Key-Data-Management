"""
WeRead 数据同步脚本
将 WeRead API 的划线和想法数据同步到本地 JSON 缓存。
前端页面从缓存读取，无需每次请求 API。

用法:
    python3 weread/sync_weread.py
"""

import os
import sys
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add parent dir so we can import from weread package
sys.path.insert(0, str(Path(__file__).parent))

from weread_api import WereadAPI


def load_cookies():
    cookie_path = Path(__file__).parent / "cookies.txt"
    if not cookie_path.exists():
        print("Error: cookies.txt not found.")
        return None
    with open(cookie_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        lines = [l for l in content.splitlines() if not l.startswith("#") and l.strip()]
        return "".join(lines)


def sync_book(api, book):
    """Fetch highlights and reviews for a single book."""
    book_id = book.get("bookId")
    book_info = book.get("book", {})
    title = book_info.get("title", "Unknown")

    try:
        highlights_resp = api.get_highlights(book_id)
        reviews_resp = api.get_reviews(book_id)

        # Check for API errors
        if highlights_resp and "errCode" in highlights_resp:
            err_msg = highlights_resp.get("errMsg", "Unknown")
            print(f"  ✗ {title}: API Error - {err_msg}")
            return book_id, None

        highlights = []
        if highlights_resp and "updated" in highlights_resp:
            for item in highlights_resp["updated"]:
                highlights.append({
                    "text": item.get("markText", ""),
                    "chapter": item.get("chapterUid", 0),
                    "createTime": item.get("createTime", 0),
                })

        reviews = []
        if reviews_resp and "reviews" in reviews_resp:
            for item in reviews_resp["reviews"]:
                review = item.get("review", {})
                reviews.append({
                    "content": review.get("content", ""),
                    "createTime": review.get("createTime", 0),
                })

        print(f"  ✓ {title}: {len(highlights)} 划线, {len(reviews)} 想法")
        return book_id, {
            "title": title,
            "highlights": highlights,
            "reviews": reviews,
            "syncedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        print(f"  ✗ {title}: {e}")
        return book_id, None


def main():
    cookie_str = load_cookies()
    if not cookie_str:
        print("请先将 Cookie 粘贴到 weread/cookies.txt")
        return False

    api = WereadAPI(cookie_str=cookie_str)

    print("正在获取书架列表...")
    notebooks = api.get_notebooks()
    if not notebooks:
        print("未找到任何笔记本，Cookie 可能已过期。")
        return False

    print(f"找到 {len(notebooks)} 本书，开始同步划线和想法...\n")

    # Load existing cache (merge, don't overwrite on partial failure)
    cache_dir = Path(__file__).parent / "cache"
    cache_dir.mkdir(exist_ok=True)
    cache_path = cache_dir / "highlights.json"

    existing_cache = {}
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                existing_cache = json.load(f)
        except Exception:
            existing_cache = {}

    # Sync each book (parallel for speed)
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(sync_book, api, book) for book in notebooks]
        for future in futures:
            book_id, data = future.result()
            if data is not None:
                results[str(book_id)] = data

    # Merge: update existing cache with new data, keep old entries
    for book_id, data in results.items():
        existing_cache[book_id] = data

    # Add metadata
    existing_cache["_meta"] = {
        "lastSyncAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "totalBooks": len(existing_cache) - 1,  # exclude _meta
    }

    # Write cache
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(existing_cache, f, ensure_ascii=False, indent=2)

    success_count = len(results)
    fail_count = len(notebooks) - success_count
    print(f"\n同步完成！成功 {success_count} 本，失败 {fail_count} 本。")
    print(f"缓存已保存到: {cache_path}")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
