import os
import re
import time
from pathlib import Path
from weread_api import WereadAPI

def load_cookies():
    cookie_path = Path(__file__).parent / "cookies.txt"
    if not cookie_path.exists():
        return None
    with open(cookie_path, 'r', encoding='utf-8') as f:
        # Parse custom format clean
        content = f.read().strip()
        lines = [l for l in content.splitlines() if not l.startswith("#") and l.strip()]
        return "".join(lines)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def format_timestamp(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

def main():
    cookie_str = load_cookies()
    if not cookie_str:
        print("Error: cookies.txt not found")
        return

    api = WereadAPI(cookie_str=cookie_str)
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    print("Fetching notebook list...")
    notebooks = api.get_notebooks()
    print(f"Found {len(notebooks)} books.")

    for book in notebooks:
        book_id = book.get("bookId")
        book_info = book.get("book")
        title = book_info.get("title")
        author = book_info.get("author")
        cover = book_info.get("cover")
        
        print(f"Exporting: {title}...")
        
        
        # Fetch details
        highlights = api.get_highlights(book_id)
        reviews = api.get_reviews(book_id)
        progress = api.get_progress(book_id)
        
        # Parse progress
        reading_time = 0
        progress_val = 0
        if progress and "book" in progress:
            data = progress["book"]
            reading_time = data.get("readingTime", 0)
            progress_val = data.get("progress", 0)
            
        # Format duration
        hours = reading_time // 3600
        mins = (reading_time % 3600) // 60
        duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

        # Prepare Markdown content
        lines = []
        lines.append(f"# {title}")
        lines.append(f"**Author**: {author}")
        lines.append(f"**Cover**: ![]({cover})")
        lines.append(f"**Progress**: {progress_val}%")
        lines.append(f"**Reading Time**: {duration_str}")
        lines.append(f"**Exported**: {time.strftime('%Y-%m-%d')}")
        lines.append("\n## Highlights\n")
        
        # Combine highlights and reviews if needed, or just list them
        # Usually highlights are 'markText'
        
        if highlights and "updated" in highlights:
            # Sort by createTime
            marks = highlights.get("updated", [])
            marks.sort(key=lambda x: x.get("createTime", 0))
            
            for mark in marks:
                text = mark.get("markText")
                if text:
                    lines.append(f"> {text}")
                    # Check if there is a review/thought attached to this highlight?
                    # In Weread structure, reviews can be separate or attached.
                    # Simple approach: List highlights, then List reviews.
                    lines.append(f"") # empty line
        
        if reviews and reviews.get("reviews"):
            lines.append("\n## Reviews\n")
            revs = reviews.get("reviews", [])
            revs.sort(key=lambda x: x.get("createTime", 0))
            
            for rev in revs:
                content = rev.get("review", {}).get("content")
                if content:
                    lines.append(f"- {content}")
                    lines.append("")

        # Write to file
        filename = f"{sanitize_filename(title)}.md"
        with open(output_dir / filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
    print(f"Exported {len(notebooks)} files to {output_dir}")

if __name__ == "__main__":
    main()
