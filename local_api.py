from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import csv
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from weread.weread_api import WereadAPI
from weread.scan import load_cookies

HOST = "0.0.0.0"
PORT = 8001
OUTPUT_DIR = Path(__file__).resolve().parent / "video"


class Handler(SimpleHTTPRequestHandler):
    def _send(self, code: int, body: str):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/weread':
            self.handle_weread()
        elif parsed_path.path == '/api/weread/link':
            params = parse_qs(parsed_path.query)
            book_id = params.get('bookId', [None])[0]
            self.handle_weread_link(book_id)
        elif parsed_path.path == '/api/weread/highlights':
            params = parse_qs(parsed_path.query)
            book_id = params.get('bookId', [None])[0]
            self.handle_weread_highlights(book_id)
        elif parsed_path.path == '/api/weread/sync':
            self.handle_weread_sync()
        else:
            super().do_GET()

    WEREAD_CACHE = {"data": None, "timestamp": 0}
    CACHE_DURATION = 1800  # 30 minutes

    def handle_weread(self):
        """Read book shelf from local cache (no API call, no cookie needed)."""
        cache_path = Path(__file__).parent / "weread" / "cache" / "books.json"

        if not cache_path.exists():
            self._send_error_json(
                "本地缓存不存在，请先运行同步: python3 weread/sync_weread.py"
            )
            return

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                books_data = json.load(f)
            self._send_json(books_data)
        except Exception as e:
            print(f"Error reading books cache: {e}")
            self._send_error_json(str(e))

    def handle_weread_link(self, book_id):
        if not book_id:
            self._send_error_json("Missing bookId")
            return
            
        try:
            from weread.scan import load_cookies
            from weread.weread_api import WereadAPI
            
            cookie_str = load_cookies()
            api = WereadAPI(cookie_str=cookie_str)
            
            detail = api.get_book_detail(book_id)
            if detail and "encodeId" in detail:
                 url = f"https://weread.qq.com/web/reader/{detail['encodeId']}"
                 self._send_json({"url": url, "encryptedBookId": detail['encodeId']})
            else:
                 # Fallback
                 self._send_json({"url": f"https://weread.qq.com/web/reader/{book_id}", "encryptedBookId": book_id})
        except Exception as e:
            print(f"Error fetching link: {e}")
            self._send_error_json(str(e))

    def handle_weread_highlights(self, book_id):
        """Read highlights from local cache (no API call, no cookie needed)."""
        if not book_id:
            self._send_error_json("Missing bookId")
            return

        cache_path = Path(__file__).parent / "weread" / "cache" / "highlights.json"

        if not cache_path.exists():
            self._send_error_json(
                "本地缓存不存在，请先运行同步: python3 weread/sync_weread.py"
            )
            return

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)

            book_data = cache.get(str(book_id))
            if not book_data or str(book_id) == "_meta":
                self._send_json({"highlights": [], "reviews": []})
                return

            self._send_json({
                "highlights": book_data.get("highlights", []),
                "reviews": book_data.get("reviews", []),
                "syncedAt": book_data.get("syncedAt", ""),
            })
        except Exception as e:
            print(f"Error reading cache: {e}")
            self._send_error_json(str(e))

    def handle_weread_sync(self):
        """Trigger a full sync from WeRead API to local cache."""
        import subprocess
        try:
            sync_script = Path(__file__).parent / "weread" / "sync_weread.py"
            result = subprocess.run(
                ["python3", str(sync_script)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(Path(__file__).parent),
            )
            if result.returncode == 0:
                self._send_json({
                    "success": True,
                    "message": "同步完成",
                    "output": result.stdout,
                })
            else:
                self._send_error_json(
                    f"同步失败: {result.stderr or result.stdout}"
                )
        except subprocess.TimeoutExpired:
            self._send_error_json("同步超时（120s）")
        except Exception as e:
            print(f"Sync error: {e}")
            self._send_error_json(str(e))


    def _send_json(self, data):
        body = json.dumps(data, ensure_ascii=False)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def _send_error_json(self, message):
        self._send_json({"error": message})

    def do_POST(self):
        if self.path != "/author":
            self._send(404, "Not Found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send(400, "Invalid Content-Length")
            return

        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send(400, "Invalid JSON")
            return

        if self.path == "/api/health":
            self.handle_health(payload)
            return

        author_id = str(payload.get("author_id", "")).strip()
        if not author_id:
            self._send(400, "author_id is required")
            return

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        target = OUTPUT_DIR / f"{author_id}.csv"
        if not target.exists():
            target.write_text("author_id\n" + author_id + "\n", encoding="utf-8")
        self._send(200, "已收到")

    def handle_health(self, payload):
        if isinstance(payload, list):
            success_count = 0
            for item in payload:
                if self._process_single_health_payload(item):
                    success_count += 1
            self._send(200, f"Batch processed {success_count}/{len(payload)} items")
        else:
            if self._process_single_health_payload(payload):
                self._send(200, "Saved")
            else:
                self._send(400, "Failed to save payload")

    def _process_single_health_payload(self, payload: dict) -> bool:
        metric_type = payload.get("type")
        data_list = payload.get("data")
        
        if not metric_type or not data_list:
             if not metric_type and isinstance(payload, dict):
                 metric_type = "generic"
                 data_list = [payload]
             else:
                 return False

        data_list = data_list if isinstance(data_list, list) else [data_list]
        if not data_list:
            return False

        health_dir = Path(__file__).resolve().parent / "health" / "data"
        health_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{metric_type}_daily.csv"
        csv_path = health_dir / filename
        
        write_header = not csv_path.exists()
        keys = data_list[0].keys()
        
        try:
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                if write_header:
                    writer.writeheader()
                for row in data_list:
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"Error writing {filename}: {e}")
            return False

    def log_message(self, format, *args):  # silence default logging
        return


if __name__ == "__main__":
    from http.server import ThreadingHTTPServer
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving on http://{HOST}:{PORT}")
    server.serve_forever()
