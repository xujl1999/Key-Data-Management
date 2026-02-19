from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
from pathlib import Path

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
