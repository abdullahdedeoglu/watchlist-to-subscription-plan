#!/usr/bin/env python
"""Watchlist -> Abonelik Plani icin surukle-birak web arayuzu.

Kullanim:
    python server.py

Tarayicida otomatik olarak http://localhost:8765 acilir. CSV dosyasini
sayfaya surukleyip birakinca ayni core.py mantigi calisir ve sonuc
platform bazli gorsel kartlar halinde gosterilir. Kapatmak icin bu
terminal penceresini kapat / Ctrl+C.
"""

import json
import sys
import threading
import time
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import core

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

WEB_DIR = Path(__file__).parent / "web"
LAST_WATCHLIST_FILE = Path(__file__).parent / "last_watchlist.csv"
HOST = "127.0.0.1"
PORT = 8765

JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()

STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}


def run_job(job_id: str, csv_text: str, country: str, owned_platforms: list) -> None:
    def progress(done: int, total: int, title: str) -> None:
        with JOBS_LOCK:
            JOBS[job_id].update(done=done, total=total, current=title)

    try:
        plan = core.process(csv_text, country=country, progress=progress, owned_platforms=owned_platforms)
        with JOBS_LOCK:
            JOBS[job_id].update(status="done", result=plan)
    except Exception as exc:
        with JOBS_LOCK:
            JOBS[job_id].update(status="error", error=str(exc))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # sessiz terminal, hatalari yine de gorecegiz

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]

        if path in STATIC_FILES:
            filename, content_type = STATIC_FILES[path]
            file_path = WEB_DIR / filename
            body = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path.startswith("/api/status/"):
            job_id = path.rsplit("/", 1)[-1]
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                snapshot = dict(job) if job else None
            if snapshot is None:
                self._send_json({"error": "job bulunamadi"}, status=404)
            else:
                self._send_json(snapshot)
            return

        if path == "/api/countries":
            countries = [
                {"code": code, "name": name, "language": lang}
                for code, (name, lang) in core.COUNTRIES.items()
            ]
            self._send_json({"countries": countries, "default": core.DEFAULT_COUNTRY})
            return

        if path == "/api/last-watchlist":
            if LAST_WATCHLIST_FILE.exists():
                self._send_json({"csv": LAST_WATCHLIST_FILE.read_text(encoding="utf-8")})
            else:
                self._send_json({"csv": None})
            return

        self._send_json({"error": "bulunamadi"}, status=404)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_POST(self):
        if self.path == "/api/rematch":
            body = self._read_json_body()
            title = body.get("title", "")
            year = body.get("year", "")
            country = (body.get("country") or core.DEFAULT_COUNTRY).upper()
            language = core.language_for(country)
            candidates, error = core.search_candidates(title, country, language)
            self._send_json({"candidates": candidates, "error": error})
            return

        if self.path == "/api/confirm-match":
            body = self._read_json_body()
            uri = body.get("uri", "")
            title = body.get("title", "")
            year = body.get("year", "")
            country = (body.get("country") or core.DEFAULT_COUNTRY).upper()
            candidate = body.get("candidate") or {}

            if not uri or not candidate:
                self._send_json({"error": "uri ve candidate gerekli"}, status=400)
                return

            cache = core.load_cache(core.CACHE_FILE)
            entry = core.confirm_match(cache, uri, title, year, country, candidate, core.CACHE_FILE)
            self._send_json({"ok": True, "entry": entry})
            return

        if self.path == "/api/upload":
            body = self._read_json_body()
            csv_text = body.get("csv", "")
            country = (body.get("country") or core.DEFAULT_COUNTRY).upper()
            owned_platforms = body.get("owned_platforms") or []

            if country not in core.COUNTRIES:
                self._send_json({"error": f"bilinmeyen ulke kodu: {country}"}, status=400)
                return

            LAST_WATCHLIST_FILE.write_text(csv_text, encoding="utf-8")

            job_id = uuid.uuid4().hex
            with JOBS_LOCK:
                JOBS[job_id] = {
                    "status": "running",
                    "done": 0,
                    "total": 0,
                    "current": "",
                    "result": None,
                    "error": None,
                }
            thread = threading.Thread(target=run_job, args=(job_id, csv_text, country, owned_platforms), daemon=True)
            thread.start()

            self._send_json({"job_id": job_id})
            return

        self._send_json({"error": "bulunamadi"}, status=404)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print(f"Sunucu calisiyor: {url}")
    print("Kapatmak icin bu pencereyi kapat ya da Ctrl+C.")
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nKapatiliyor...")
        server.shutdown()


if __name__ == "__main__":
    main()
