"""
WeRead 数据同步脚本
将 WeRead API 的书架、划线和想法数据同步到本地 JSON 缓存。
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

CACHE_DIR = Path(__file__).parent / "cache"


def load_cookies():
    cookie_path = Path(__file__).parent / "cookies.txt"
    if not cookie_path.exists():
        print("Error: cookies.txt not found.")
        return None
    with open(cookie_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        lines = [l for l in content.splitlines() if not l.startswith("#") and l.strip()]
        return "".join(lines)


def sync_book_shelf(api, notebooks):
    """Sync book shelf data (title, author, cover, progress, encodeId)."""
    print("同步书架信息...")

    def fetch_book_info(item):
        book_id = item.get("bookId")
        book_info = item.get("book", {})
        title = book_info.get("title", "Unknown")
        author = book_info.get("author", "Unknown")
        cover = book_info.get("cover", "")

        progress_val = 0
        reading_time_str = ""
        encrypted_id = book_id

        try:
            progress_info = api.get_progress(book_id)
            detail_info = api.get_book_detail(book_id)

            if detail_info and "encodeId" in detail_info:
                encrypted_id = detail_info["encodeId"]

            if progress_info and "book" in progress_info:
                data = progress_info["book"]
                reading_time = data.get("readingTime", 0)
                progress_val = data.get("progress", 0)
                hours = reading_time // 3600
                mins = (reading_time % 3600) // 60
                reading_time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
        except Exception as e:
            print(f"  ⚠ {title}: {e}")

        print(f"  ✓ {title}")
        return {
            "title": title,
            "author": author,
            "cover": cover,
            "progress": progress_val,
            "readingTime": reading_time_str,
            "bookId": book_id,
            "encryptedBookId": encrypted_id,
            "updated": item.get("updated", 0),
        }

    with ThreadPoolExecutor(max_workers=10) as executor:
        books = list(executor.map(fetch_book_info, notebooks))

    books_data = {
        "books": books,
        "all_books": [],
        "updatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    books_path = CACHE_DIR / "books.json"
    with open(books_path, "w", encoding="utf-8") as f:
        json.dump(books_data, f, ensure_ascii=False, indent=2)

    print(f"  书架信息已缓存 ({len(books)} 本)\n")
    return books_data


def sync_highlights(api, notebooks):
    """Sync highlights and reviews for all books."""
    print("同步划线和想法...")

    def sync_book(book):
        book_id = book.get("bookId")
        book_info = book.get("book", {})
        title = book_info.get("title", "Unknown")

        try:
            highlights_resp = api.get_highlights(book_id)
            reviews_resp = api.get_reviews(book_id)

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

    # Load existing cache
    cache_path = CACHE_DIR / "highlights.json"
    existing_cache = {}
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                existing_cache = json.load(f)
        except Exception:
            existing_cache = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(sync_book, book) for book in notebooks]
        results = {}
        for future in futures:
            book_id, data = future.result()
            if data is not None:
                results[str(book_id)] = data

    # Merge
    for book_id, data in results.items():
        existing_cache[book_id] = data

    existing_cache["_meta"] = {
        "lastSyncAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "totalBooks": len(existing_cache) - 1,
    }

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(existing_cache, f, ensure_ascii=False, indent=2)

    success_count = len(results)
    fail_count = len(notebooks) - success_count
    print(f"  划线同步完成: 成功 {success_count}, 失败 {fail_count}\n")
    return success_count, fail_count


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

    print(f"找到 {len(notebooks)} 本书\n")

    CACHE_DIR.mkdir(exist_ok=True)

    # Sync both shelf and highlights
    sync_book_shelf(api, notebooks)
    success, fail = sync_highlights(api, notebooks)

    print(f"全部同步完成！缓存目录: {CACHE_DIR}")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

