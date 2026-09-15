"""Dosya depolama soyutlamasi.

Yerelde (UPSTASH_REDIS_REST_URL ortam degiskeni yoksa) her sey bugunku gibi
proje klasorundeki dosyalara yazilir - hicbir davranis degismez, sync.py bu
modulu hic kullanmaz. Prod'da (Render gibi diski kalici olmayan bir yerde
calisirken) ayni "Path" benzeri arayuz, verileri Upstash Redis'e (REST API
uzerinden) yazan RedisPath ile karsilanir. core.py ve server.py, aldiklari
nesnenin gercek bir Path mi RedisPath mi oldugunu bilmek zorunda degil -
sadece .exists() / .read_text() / .write_text() / .unlink() kullanirlar.
"""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent


def _clean_env_value(value: str) -> str:
    """Upstash panelindeki '.env' formatli satirlar (KEY="deger") oldugu gibi
    kopyala-yapistirilirsa (isim + tirnaklarla birlikte) ortaya cikan yaygin
    hatayi tolere eder - sadece gercek degeri cikarir."""
    value = value.strip()
    if "=" in value and not value.startswith(("http://", "https://")):
        value = value.split("=", 1)[1]
    return value.strip().strip('"').strip("'")


UPSTASH_URL = _clean_env_value(os.environ.get("UPSTASH_REDIS_REST_URL", "")).rstrip("/")
UPSTASH_TOKEN = _clean_env_value(os.environ.get("UPSTASH_REDIS_REST_TOKEN", ""))
IS_PRODUCTION = bool(UPSTASH_URL and UPSTASH_TOKEN)


def _upstash_request(method: str, path: str, body: bytes | None = None) -> dict:
    req = urllib.request.Request(
        f"{UPSTASH_URL}/{path}",
        data=body,
        method=method,
        headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Upstash istegi basarisiz ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Upstash'e baglanilamadi: {exc.reason}") from exc


class RedisPath:
    """pathlib.Path'in bu projede kullanilan kucuk bir altkumesini taklit eder."""

    def __init__(self, key: str):
        self.key = key

    def exists(self) -> bool:
        result = _upstash_request("GET", f"get/{self.key}")
        return result.get("result") is not None

    def read_text(self, encoding: str = "utf-8") -> str:
        result = _upstash_request("GET", f"get/{self.key}")
        value = result.get("result")
        if value is None:
            raise FileNotFoundError(self.key)
        return value

    def write_text(self, text: str, encoding: str = "utf-8") -> None:
        _upstash_request("POST", f"set/{self.key}", body=text.encode("utf-8"))

    def unlink(self, missing_ok: bool = False) -> None:
        _upstash_request("POST", f"del/{self.key}")

    def __str__(self) -> str:
        return f"redis:{self.key}"

    def __fspath__(self) -> str:
        raise NotImplementedError("RedisPath disk yolu degil, dogrudan acilamaz")


def make_path(relative_key: str) -> "Path | RedisPath":
    """relative_key ornek: 'justwatch_cache.json' ya da 'sessions/<id>/last_watchlist.csv'."""
    if IS_PRODUCTION:
        return RedisPath(relative_key.replace("/", ":"))
    local_path = BASE_DIR / relative_key
    local_path.parent.mkdir(parents=True, exist_ok=True)
    return local_path
