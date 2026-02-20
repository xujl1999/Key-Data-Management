from weread_api import WereadAPI
from scan import load_cookies
import json

def main():
    cookie_str = load_cookies()
    api = WereadAPI(cookie_str=cookie_str)
    
    # Get notebooks first to find a book ID
    notebooks = api.get_notebooks()
    target_book = None
    for book in notebooks:
        if "置身事内" in book["book"]["title"]:
            target_book = book
            break
            
    if not target_book:
        print("Book not found")
        return

    book_id = target_book["bookId"]
    print(f"Checking progress for {target_book['book']['title']} ({book_id})")
    
    prog = api.get_progress(book_id)
    print(json.dumps(prog, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
