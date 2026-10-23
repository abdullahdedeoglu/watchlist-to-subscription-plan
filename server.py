#!/usr/bin/env python
"""Watchlist -> Abonelik Plani icin surukle-birak web arayuzu.

Kullanim:
    python server.py

Tarayicida otomatik olarak http://localhost:8765 acilir. CSV dosyasini
sayfaya surukleyip birakinca ayni core.py mantigi calisir ve sonuc
platform bazli gorsel kartlar halinde gosterilir. Kapatmak icin bu
terminal penceresini kapat / Ctrl+C.
"""

import http.cookies
import json
import os
import re
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import core
import storage

try:
    # line_buffering=True: Render (ve genel olarak dosyaya/pipe'a yonlendirilmis
    # her stdout) print() ciktisini varsayilan olarak blok halinde tamponluyor -
    # gercek bir hata olustugunda log ekraninda hemen gorunmuyor (bazen hic
    # gorunmuyor), sadece traceback.print_exc()'in ayri kanali (stderr) hemen
    # cikiyor. Satir satir flush ederek ikisini de anlik gorebiliyoruz.
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except AttributeError:
    pass

WEB_DIR = Path(__file__).parent / "web"
PORT = int(os.environ.get("PORT", 8765))
# PORT ortam degiskeni sadece bir hosting platformunda (Render vb.) calisirken
# gelir - yerel kullanimda yokluk, 127.0.0.1'e (ve tarayiciyi otomatik acmaya)
# geri duser.
HOST = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"

SESSION_COOKIE_NAME = "wp_session"
SESSION_ID_RE = re.compile(r"^[0-9a-f]{32}$")

# Hazir listeler (dropzone'daki "IMDb Top 250" / "Letterboxd Top 500" butonlari)
# kendi ayri, PAYLASIMLI (session'a gore degil) JustWatch cache dosyalarini
# kullanir - boylece kullanicinin gercek watchlist'inin cache'ine
# (justwatch_cache.json) karismaz ve "Watchlist'ten cikmis" karsilastirmasini
# bozmaz. Bu cache'ler kasitli olarak global: bir filmi kim ararsa arasin
# herkes icin cache'lenir, kullanici sayisi arttikca JustWatch'a giden toplam
# istek artmaz.
PRESET_CACHE_FILES = {
    "imdb-top-250": storage.make_path("justwatch_cache_preset_imdb-top-250.json"),
    "letterboxd-top-500": storage.make_path("justwatch_cache_preset_letterboxd-top-500.json"),
}


def resolve_cache_file(preset: str | None):
    if preset is None:
        return storage.make_path("justwatch_cache.json")
    cache_file = PRESET_CACHE_FILES.get(preset)
    if cache_file is None:
        raise ValueError(f"bilinmeyen preset: {preset}")
    return cache_file


def session_watchlist_file(session_id: str):
    return storage.make_path(f"sessions/{session_id}/last_watchlist.csv")


def session_preset_file(session_id: str):
    return storage.make_path(f"sessions/{session_id}/last_preset.txt")


# Gercek watchlist ve her preset icin, CSV'den bagimsiz elle eklenen/cikarilan
# filmleri tutar (bkz. core.apply_overrides). Boylece kullanici Letterboxd'dan
# tekrar export almadan liste uzerinde oynama yapabilir. Bu, cache'in aksine,
# ziyaretcinin kendi session'ina ozeldir - baskasinin eklediginin sende
# gorunmemesi gerekir.
def resolve_overrides_file(session_id: str, preset: str | None):
    if preset is None:
        return storage.make_path(f"sessions/{session_id}/manual_overrides.json")
    if preset not in PRESET_CACHE_FILES:
        raise ValueError(f"bilinmeyen preset: {preset}")
    return storage.make_path(f"sessions/{session_id}/manual_overrides_preset_{preset}.json")


def load_overrides(overrides_file) -> dict:
    if not overrides_file.exists():
        return {"added": [], "removed": []}
    return json.loads(overrides_file.read_text(encoding="utf-8"))


def save_overrides(overrides_file, overrides: dict) -> None:
    overrides_file.write_text(json.dumps(overrides, ensure_ascii=False, indent=2), encoding="utf-8")


def _extract_session_id(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None
    jar = http.cookies.SimpleCookie()
    try:
        jar.load(cookie_header)
    except Exception:
        return None
    morsel = jar.get(SESSION_COOKIE_NAME)
    if morsel and SESSION_ID_RE.match(morsel.value):
        return morsel.value
    return None


JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()

# Site icinden geri bildirim formu - Resend'in HTTP API'siyle
# watchplan.support@gmail.com adresine mail atar. Once smtplib/Gmail SMTP
# denendi ama Render'in ucretsiz planinda giden SMTP portlari (25/465/587)
# tamamen blok - bkz. https://render.com/changelog/free-web-services-will-no-longer-allow-outbound-traffic-to-smtp-ports
# Resend duz bir HTTPS istegi oldugu icin bu kisitlamaya takilmiyor.
# RESEND_API_KEY tanimli degilse (yerel gelistirme) gercekten istek atmaz,
# sadece konsola yazdirir - boylece gercek kimlik bilgisi olmadan da test edilebilir.
FEEDBACK_TO_EMAIL = "watchplan.support@gmail.com"
FEEDBACK_FROM_EMAIL = "WatchPlan <onboarding@resend.dev>"
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

FEEDBACK_MAX_LENGTH = 3000
FEEDBACK_RATE_LIMIT = 5
FEEDBACK_RATE_WINDOW = 3600  # saniye

_FEEDBACK_TIMESTAMPS: dict[str, list[float]] = {}
_FEEDBACK_LOCK = threading.Lock()


def _feedback_rate_limited(session_id: str) -> bool:
    now = time.time()
    with _FEEDBACK_LOCK:
        recent = [t for t in _FEEDBACK_TIMESTAMPS.get(session_id, []) if now - t < FEEDBACK_RATE_WINDOW]
        limited = len(recent) >= FEEDBACK_RATE_LIMIT
        recent.append(now)
        _FEEDBACK_TIMESTAMPS[session_id] = recent
        return limited


def send_feedback_email(message: str, movie: dict | None) -> None:
    lines = [message]
    if movie:
        lines.append("")
        lines.append("--- Ilgili film ---")
        lines.append(f"Baslik: {movie.get('title')} ({movie.get('year')})")
        if movie.get("matched_title"):
            lines.append(f"JustWatch eslesmesi: {movie.get('matched_title')} ({movie.get('matched_year')})")
        if movie.get("uri"):
            lines.append(f"Letterboxd URI: {movie.get('uri')}")
    body = "\n".join(lines)

    if not RESEND_API_KEY:
        print("=== GERI BILDIRIM (RESEND_API_KEY tanimli degil, sadece logluyorum) ===")
        print(body)
        print("========================================================================")
        return

    payload = json.dumps(
        {
            "from": FEEDBACK_FROM_EMAIL,
            "to": [FEEDBACK_TO_EMAIL],
            "subject": "WatchPlan Geri Bildirim" + (" (film ile ilgili)" if movie else ""),
            "text": body,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
            # urllib'in varsayilan "Python-urllib/x.y" User-Agent'i Resend'in
            # onundeki Cloudflare bot korumasina takiliyor (403, "error code:
            # 1010") - normal bir deger vermek yetiyor.
            "User-Agent": "WatchPlan/1.0 (+https://watchplan.onrender.com)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
    except urllib.error.HTTPError as exc:
        # Resend hata govdesinde (JSON) neden reddedildigini aciklar -
        # bunu loglamazsak sadece "403 Forbidden" gorup sebebi bilemeyiz.
        print(f"Resend hatasi ({exc.code}): {exc.read().decode('utf-8', errors='replace')}")
        raise

STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
    "/particles.js": ("particles.js", "application/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/robots.txt": ("robots.txt", "text/plain; charset=utf-8"),
    # Google Search Console sahiplik dogrulamasi - silinirse dogrulama duser
    "/google8fb3670c7bdfd470.html": ("google8fb3670c7bdfd470.html", "text/html; charset=utf-8"),
    "/sitemap.xml": ("sitemap.xml", "application/xml; charset=utf-8"),
    "/site.webmanifest": ("site.webmanifest", "application/manifest+json; charset=utf-8"),
    "/favicon.ico": ("favicon.ico", "image/x-icon"),
    "/assets/apple-touch-icon.png": ("assets/apple-touch-icon.png", "image/png"),
    "/assets/favicon-32.png": ("assets/favicon-32.png", "image/png"),
    "/assets/favicon-48.png": ("assets/favicon-48.png", "image/png"),
    "/assets/icon-192.png": ("assets/icon-192.png", "image/png"),
    "/assets/icon-512.png": ("assets/icon-512.png", "image/png"),
    "/assets/favicon-16.png": ("assets/favicon-16.png", "image/png"),
    "/assets/logo-mark.webp": ("assets/logo-mark.webp", "image/webp"),
    "/assets/og-image.jpg": ("assets/og-image.jpg", "image/jpeg"),
    "/assets/grain.jpg": ("assets/grain.jpg", "image/jpeg"),
    "/assets/beam-v2.webp": ("assets/beam-v2.webp", "image/webp"),
    "/assets/edge-burn.webp": ("assets/edge-burn.webp", "image/webp"),
    "/assets/wordmark.webp": ("assets/wordmark.webp", "image/webp"),
    "/assets/edge-stain-left.webp": ("assets/edge-stain-left.webp", "image/webp"),
    "/assets/edge-stain-right.webp": ("assets/edge-stain-right.webp", "image/webp"),
    "/assets/film-strip.webp": ("assets/film-strip.webp", "image/webp"),
    "/assets/ticket-frame-v3.webp": ("assets/ticket-frame-v3.webp", "image/webp"),
    "/assets/modal-edge.webp": ("assets/modal-edge.webp", "image/webp"),
    "/assets/modal-edge-right.webp": ("assets/modal-edge-right.webp", "image/webp"),
    "/assets/video-cover.jpg": ("assets/video-cover.jpg", "image/jpeg"),
    "/presets/imdb-top-250.csv": ("presets/imdb-top-250.csv", "text/csv; charset=utf-8"),
    "/presets/letterboxd-top-500.csv": ("presets/letterboxd-top-500.csv", "text/csv; charset=utf-8"),
}


def run_job(
    job_id: str, csv_text: str, country: str, owned_platforms: list, cache_file: Path, overrides: dict
) -> None:
    def progress(done: int, total: int, title: str, phase: str = "search") -> None:
        with JOBS_LOCK:
            JOBS[job_id].update(done=done, total=total, current=title, phase=phase)

    try:
        plan = core.process(
            csv_text,
            country=country,
            cache_file=cache_file,
            progress=progress,
            owned_platforms=owned_platforms,
            overrides=overrides,
            popular_index_file=storage.make_path(f"justwatch_popular_index_{country}.json"),
        )
        with JOBS_LOCK:
            JOBS[job_id].update(status="done", result=plan)
    except Exception as exc:
        with JOBS_LOCK:
            JOBS[job_id].update(status="error", error=str(exc))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # sessiz terminal, hatalari yine de gorecegiz

    def _ensure_session(self) -> None:
        # Her ziyaretcinin gorunmez bir session cookie'si olur - watchlist'i
        # ve elle ekledigi/cikardigi filmler bu kimlige gore ayrilir. JustWatch
        # cache'i ise kasitli olarak buna bagli degil, herkes arasinda paylasilir.
        sid = _extract_session_id(self.headers.get("Cookie"))
        if sid is None:
            sid = uuid.uuid4().hex
            self._new_session = True
        else:
            self._new_session = False
        self.session_id = sid

    def _set_cookie_header(self) -> None:
        if getattr(self, "_new_session", False):
            self.send_header(
                "Set-Cookie",
                f"{SESSION_COOKIE_NAME}={self.session_id}; Path=/; Max-Age=31536000; HttpOnly; SameSite=Lax",
            )

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._set_cookie_header()
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        # UptimeRobot vb. uptime izleyiciler varsayilan olarak HEAD istegi
        # gonderiyor - http.server bunu tanimadigi metod sayip 501 Not
        # Implemented dondururdu (izleyicide "down" gibi gorunuyordu).
        try:
            self._ensure_session()
            self.send_response(200)
            self._set_cookie_header()
            self.end_headers()
        except Exception:
            traceback.print_exc()
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        try:
            self._handle_get()
        except Exception as exc:
            traceback.print_exc()
            self._send_json({"error": f"sunucu hatasi: {exc}"}, status=500)

    def _handle_get(self):
        self._ensure_session()
        path = self.path.split("?")[0]

        if path in STATIC_FILES:
            filename, content_type = STATIC_FILES[path]
            file_path = WEB_DIR / filename
            body = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            if path.startswith("/assets/") or path == "/favicon.ico":
                # Gorseller nadiren degisir; bir gun onbellekte kalsin.
                self.send_header("Cache-Control", "public, max-age=86400")
            self._set_cookie_header()
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
                {"code": code, "name_tr": info["tr"], "name_en": info["en"], "language": info["lang"]}
                for code, info in core.COUNTRIES.items()
            ]
            self._send_json({"countries": countries, "default": core.DEFAULT_COUNTRY})
            return

        if path == "/api/last-watchlist":
            watchlist_file = session_watchlist_file(self.session_id)
            preset_file = session_preset_file(self.session_id)
            if watchlist_file.exists():
                preset = preset_file.read_text(encoding="utf-8").strip() if preset_file.exists() else None
                self._send_json({"csv": watchlist_file.read_text(encoding="utf-8"), "preset": preset or None})
            else:
                self._send_json({"csv": None, "preset": None})
            return

        self._send_json({"error": "bulunamadi"}, status=404)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_POST(self):
        try:
            self._handle_post()
        except Exception as exc:
            traceback.print_exc()
            self._send_json({"error": f"sunucu hatasi: {exc}"}, status=500)

    def _handle_post(self):
        self._ensure_session()
        if self.path == "/api/rematch":
            body = self._read_json_body()
            title = body.get("title", "")
            year = body.get("year", "")
            country = (body.get("country") or core.DEFAULT_COUNTRY).upper()
            language = core.language_for(country)
            candidates, error = core.search_candidates(title, country, language, target_year=year)
            self._send_json({"candidates": candidates, "error": error})
            return

        if self.path == "/api/confirm-match":
            body = self._read_json_body()
            uri = body.get("uri", "")
            title = body.get("title", "")
            year = body.get("year", "")
            country = (body.get("country") or core.DEFAULT_COUNTRY).upper()
            candidate = body.get("candidate") or {}
            preset = body.get("preset")

            if not uri or not candidate:
                self._send_json({"error": "uri ve candidate gerekli"}, status=400)
                return

            try:
                cache_file = resolve_cache_file(preset)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return

            cache = core.load_cache(cache_file)
            entry = core.confirm_match(cache, uri, title, year, country, candidate, cache_file)
            self._send_json({"ok": True, "entry": entry})
            return

        if self.path == "/api/clear-cache":
            # GELISTIRME ARACI - JustWatch eslestirme cache'ini sifirlar.
            # Prod'da (Upstash'e bagliyken) herkesin paylastigi cache'i rastgele
            # bir ziyaretci silemesin diye kapali.
            if storage.IS_PRODUCTION:
                self._send_json({"error": "devre disi"}, status=403)
                return
            core.save_cache({}, storage.make_path("justwatch_cache.json"))
            self._send_json({"ok": True})
            return

        if self.path == "/api/clear-watchlist":
            # Aktif watchlist'i (gercek ya da preset fark etmez) kaldirir -
            # JustWatch cache'lerine dokunmaz, sadece "hatirlanan" isareti siler.
            session_watchlist_file(self.session_id).unlink(missing_ok=True)
            session_preset_file(self.session_id).unlink(missing_ok=True)
            self._send_json({"ok": True})
            return

        if self.path == "/api/upload":
            body = self._read_json_body()
            csv_text = body.get("csv", "")
            country = (body.get("country") or core.DEFAULT_COUNTRY).upper()
            owned_platforms = body.get("owned_platforms") or []
            preset = body.get("preset")

            if country not in core.COUNTRIES:
                self._send_json({"error": f"bilinmeyen ulke kodu: {country}"}, status=400)
                return

            try:
                cache_file = resolve_cache_file(preset)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return

            # Aktif watchlist (gercek ya da preset) her zaman hatirlanir; hangi
            # preset oldugu ayri dosyada tutulur ki sayfa yeniden acildiginda
            # dogru JustWatch cache dosyasi ile eslessin. Bu, ziyaretcinin
            # session'ina ozeldir - baskasinin watchlist'i sende gorunmez.
            session_watchlist_file(self.session_id).write_text(csv_text, encoding="utf-8")
            if preset is None:
                session_preset_file(self.session_id).unlink(missing_ok=True)
            else:
                session_preset_file(self.session_id).write_text(preset, encoding="utf-8")

            overrides = load_overrides(resolve_overrides_file(self.session_id, preset))

            job_id = uuid.uuid4().hex
            with JOBS_LOCK:
                JOBS[job_id] = {
                    "status": "running",
                    "done": 0,
                    "total": 0,
                    "current": "",
                    "phase": "search",
                    "result": None,
                    "error": None,
                }
            thread = threading.Thread(
                target=run_job,
                args=(job_id, csv_text, country, owned_platforms, cache_file, overrides),
                daemon=True,
            )
            thread.start()

            self._send_json({"job_id": job_id})
            return

        if self.path == "/api/add-film":
            # CSV'den bagimsiz, elle bir film ekler: JustWatch'ta zaten aranip
            # secilmis bir "candidate" cache'e senkron eslesme olarak yazilir
            # (yeni bir arama tetiklemez), ve senkron bir "manual:" uri'si
            # overrides dosyasina eklenir ki bir sonraki process() bu filmi
            # CSV'de olmasa da listeye dahil etsin.
            body = self._read_json_body()
            title = body.get("title", "")
            year = body.get("year", "")
            country = (body.get("country") or core.DEFAULT_COUNTRY).upper()
            candidate = body.get("candidate") or {}
            preset = body.get("preset")

            if not title or not candidate:
                self._send_json({"error": "title ve candidate gerekli"}, status=400)
                return

            try:
                cache_file = resolve_cache_file(preset)
                overrides_file = resolve_overrides_file(self.session_id, preset)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return

            uri = f"manual:{uuid.uuid4().hex}"
            cache = core.load_cache(cache_file)
            core.confirm_match(cache, uri, title, year, country, candidate, cache_file)

            overrides = load_overrides(overrides_file)
            overrides.setdefault("added", []).append({"uri": uri, "title": title, "year": year})
            save_overrides(overrides_file, overrides)

            self._send_json({"ok": True, "uri": uri})
            return

        if self.path == "/api/remove-film":
            # Aktif listeden (gercek CSV satiri olsa da olmasa da) bir filmi
            # kalici olarak gizler - overrides dosyasindaki "removed" listesine
            # eklenir, boylece her CSV yuklemesinde tekrar uygulanir.
            body = self._read_json_body()
            uri = body.get("uri", "")
            preset = body.get("preset")

            if not uri:
                self._send_json({"error": "uri gerekli"}, status=400)
                return

            try:
                overrides_file = resolve_overrides_file(self.session_id, preset)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return

            overrides = load_overrides(overrides_file)
            removed = overrides.setdefault("removed", [])
            if uri not in removed:
                removed.append(uri)
            overrides["added"] = [a for a in overrides.get("added", []) if a["uri"] != uri]
            save_overrides(overrides_file, overrides)

            self._send_json({"ok": True})
            return

        if self.path == "/api/feedback":
            body = self._read_json_body()
            message = (body.get("message") or "").strip()
            movie = body.get("movie") or None

            if not message:
                self._send_json({"error": "mesaj bos olamaz"}, status=400)
                return
            if len(message) > FEEDBACK_MAX_LENGTH:
                self._send_json({"error": "mesaj cok uzun"}, status=400)
                return
            if _feedback_rate_limited(self.session_id):
                self._send_json({"error": "cok fazla istek, biraz sonra tekrar dene"}, status=429)
                return

            try:
                send_feedback_email(message, movie)
            except Exception:
                traceback.print_exc()
                self._send_json({"error": "gonderilemedi, lutfen sonra tekrar dene"}, status=500)
                return

            self._send_json({"ok": True})
            return

        self._send_json({"error": "bulunamadi"}, status=404)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    is_hosted = bool(os.environ.get("PORT"))
    url = f"http://localhost:{PORT}" if is_hosted else f"http://{HOST}:{PORT}"
    print(f"Sunucu calisiyor: {url}")
    print("Kapatmak icin bu pencereyi kapat ya da Ctrl+C.")
    if not is_hosted:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nKapatiliyor...")
        server.shutdown()


if __name__ == "__main__":
    main()
