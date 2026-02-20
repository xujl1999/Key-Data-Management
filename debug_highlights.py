
import os
import sys
import json
from weread.weread_api import WereadAPI

def load_cookies():
    cookie_path = os.path.join("weread", "cookies.txt")
    with open(cookie_path, "r", encoding="utf-8") as f:
        cookie_str = f.read().strip()
    return cookie_str

def main():
    cookie_str = load_cookies()
    print(f"Loaded cookies: {cookie_str[:20]}...")
    api = WereadAPI(cookie_str=cookie_str)
    
    ids = ["29841857", "33641196"]
    
    for book_id in ids:
        print(f"\n--- Testing Book ID: {book_id} ---")
        try:
             detail = api.get_book_detail(book_id)
             print(f"Detail Title: {detail.get('title', 'Unknown') if detail else 'None'}")
             
             hl = api.get_highlights(book_id)
             err = hl.get('errMsg', 'None') if hl else 'None'
             count = len(hl.get('updated', [])) if hl and 'updated' in hl else 0
             print(f"Highlights: {count} items. Error: {err}")
             
             rv = api.get_reviews(book_id)
             rv_count = len(rv.get('reviews', [])) if rv and 'reviews' in rv else 0
             print(f"Reviews: {rv_count} items.")
             
        except Exception as e:
             print(f"Exception: {e}")

    return
    
    # 2. Get Highlights
    print(f"Fetching highlights for {book_id}...")
    highlights = api.get_highlights(book_id)
    print(f"Raw Highlights Response: {json.dumps(highlights, indent=2, ensure_ascii=False)}")
    
    # 3. Get Reviews
    print(f"Fetching reviews for {book_id}...")
    reviews = api.get_reviews(book_id)
    print(f"Raw Reviews Response: {json.dumps(reviews, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main()
