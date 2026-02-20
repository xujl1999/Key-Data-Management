import os
import sys
from pathlib import Path


def load_cookies():
    cookie_path = Path(__file__).parent / "cookies.txt"
    if not cookie_path.exists():
        print("Error: cookies.txt not found.")
        return None
        
    with open(cookie_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        # Skip comments
        lines = [l for l in content.splitlines() if not l.startswith("#") and l.strip()]
        return "".join(lines)

def main():
    cookie_str = load_cookies()
    if not cookie_str:
        print("Please paste your cookies into weread/cookies.txt")
        return

    from weread_api import WereadAPI
    api = WereadAPI(cookie_str=cookie_str)
    
    print("Fetching notebooks...")
    notebooks = api.get_notebooks()
    
    if not notebooks:
        print("No notebooks found or cookie invalid.")
        return

    print(f"Found {len(notebooks)} books with notes.")
    
    for book in notebooks:
        book_id = book.get("bookId")
        book_info = book.get("book")
        title = book_info.get("title")
        author = book_info.get("author")
        print(f"Processing: {title} - {author}")
        
        # Get highlights
        highlights = api.get_highlights(book_id)
        if highlights:
            updated = highlights.get("updated")
            chapters = highlights.get("chapters", [])
            print(f"  - Highlights updated: {updated}")
            print(f"  - Chapters with notes: {len(chapters)}")
            
        # Get reviews
        reviews = api.get_reviews(book_id)
        if reviews and reviews.get("reviews"):
            print(f"  - Reviews: {len(reviews.get('reviews'))}")
            
    print("Done.")

if __name__ == "__main__":
    main()
