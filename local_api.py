from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8000
OUTPUT_DIR = Path(__file__).resolve().parent / "video"


class Handler(BaseHTTPRequestHandler):
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

        author_id = str(payload.get("author_id", "")).strip()
        if not author_id:
            self._send(400, "author_id is required")
            return

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        target = OUTPUT_DIR / f"{author_id}.csv"
        if not target.exists():
            target.write_text("author_id\n" + author_id + "\n", encoding="utf-8")
        self._send(200, "已收到")

    def log_message(self, format, *args):  # silence default logging
        return


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Serving on http://{HOST}:{PORT}")
    server.serve_forever()
