"""Letterboxd watchlist'ini JustWatch ile eslestiren ve aylik abonelik
planini ureten paylasilan mantik.

Hem sync.py (CLI) hem de server.py (web arayuzu) bu modulu kullanir.
"""

import csv
import io
import json
import time
from pathlib import Path

from simplejustwatchapi.justwatch import search

CACHE_FILE = Path("justwatch_cache.json")
DEFAULT_COUNTRY = "TR"
SEARCH_COUNT = 5
REQUEST_DELAY_SECONDS = 0.5

# Desteklenen ulkeler: kod -> (goruntulenen isim, JustWatch dil kodu)
COUNTRIES = {
    "TR": ("Turkiye", "tr"),
    "US": ("Amerika Birlesik Devletleri", "en"),
    "GB": ("Ingiltere", "en"),
    "DE": ("Almanya", "de"),
    "FR": ("Fransa", "fr"),
    "ES": ("Ispanya", "es"),
    "IT": ("Italya", "it"),
    "NL": ("Hollanda", "nl"),
    "PT": ("Portekiz", "pt"),
    "BR": ("Brezilya", "pt"),
    "CA": ("Kanada", "en"),
    "AU": ("Avustralya", "en"),
    "MX": ("Meksika", "es"),
    "PL": ("Polonya", "pl"),
    "SE": ("Isvec", "sv"),
    "IN": ("Hindistan", "en"),
    "JP": ("Japonya", "ja"),
    "KR": ("Guney Kore", "ko"),
    "RU": ("Rusya", "ru"),
    "AR": ("Arjantin", "es"),
}


def language_for(country: str) -> str:
    return COUNTRIES.get(country, (None, "en"))[1]


def parse_csv_text(text: str) -> list[dict]:
    rows = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        rows.append(
            {
                "date": row["Date"],
                "title": row["Name"],
                "year": row["Year"],
                "uri": row["Letterboxd URI"],
            }
        )
    return rows


def load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return parse_csv_text(f.read())


def _migrate_entry(uri: str, entry: dict) -> dict:
    """Eski format (ulke bazsiz, sadece TR icin) kaydi yeni 'by_country'
    yapisina tasir. Eski veri kaybolmasin diye TR altina yerlestirilir."""
    if "by_country" in entry:
        return entry
    return {
        "title": entry.get("title"),
        "year": entry.get("year"),
        "by_country": {
            "TR": {
                "matched_title": entry.get("matched_title"),
                "matched_year": entry.get("matched_year"),
                "poster": entry.get("poster"),
                "offers": entry.get("offers", []),
                "platforms": entry.get("platforms", []),
                "matched": entry.get("matched", False),
            }
        },
    }


def load_cache(cache_file: Path = CACHE_FILE) -> dict:
    if not cache_file.exists():
        return {}
    with open(cache_file, encoding="utf-8") as f:
        raw = json.load(f)
    return {uri: _migrate_entry(uri, entry) for uri, entry in raw.items()}


def save_cache(cache: dict, cache_file: Path = CACHE_FILE) -> None:
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2, sort_keys=True)


def flatrate_offers(entry) -> list[dict]:
    """Unique FLATRATE (abonelik) teklifleri, platform basina bir tane."""
    offers = []
    seen = set()
    for offer in entry.offers:
        if offer.monetization_type != "FLATRATE" or offer.name in seen:
            continue
        seen.add(offer.name)
        offers.append({"platform": offer.name, "url": offer.url})
    return offers


def entry_to_candidate(entry) -> dict:
    """Bir JustWatch MediaEntry'sini cache/UI'da kullanilan sozluk formuna cevirir."""
    offers = flatrate_offers(entry)
    return {
        "matched_title": entry.title,
        "matched_year": entry.release_year,
        "poster": entry.poster,
        "offers": offers,
        "platforms": [o["platform"] for o in offers],
        "matched": True,
    }


def needs_lookup(cache: dict, uri: str, country: str) -> bool:
    entry = cache.get(uri)
    if entry is None:
        return True
    return country not in entry.get("by_country", {})


def _target_year(year: str) -> int | None:
    try:
        return int(year)
    except (TypeError, ValueError):
        return None


def search_movie(title: str, year: str, country: str, language: str) -> tuple[dict | None, str | None]:
    """Returns (by_country_entry_dict, error_message)."""
    try:
        results = search(title, country=country, language=language, count=SEARCH_COUNT)
    except Exception as exc:  # network / rate limit / API errors
        return None, f"JustWatch istegi basarisiz: {exc}"

    if not results:
        return None, "JustWatch'ta sonuc bulunamadi"

    target_year = _target_year(year)

    chosen = None
    if target_year is not None:
        for entry in results:
            if entry.release_year == target_year:
                chosen = entry
                break
    if chosen is None:
        chosen = results[0]

    # Yil eslesmediyse (ya da CSV'de yil yoksa) bu, ilk sonuca dusuldugu
    # anlamina gelir - remake/ayni isimli baska film riski var, kontrol onerilir.
    needs_review = target_year is None or chosen.release_year != target_year

    candidate = entry_to_candidate(chosen)
    candidate["needs_review"] = needs_review
    candidate["manually_confirmed"] = False
    return candidate, None


def search_candidates(title: str, country: str, language: str, count: int = 8) -> tuple[list[dict], str | None]:
    """Rematch/duzeltme arayuzu icin butun aday sonuclari dondurur (otomatik secim yapmaz)."""
    try:
        results = search(title, country=country, language=language, count=count)
    except Exception as exc:
        return [], f"JustWatch istegi basarisiz: {exc}"
    if not results:
        return [], "JustWatch'ta sonuc bulunamadi"
    return [entry_to_candidate(entry) for entry in results], None


def confirm_match(cache: dict, uri: str, csv_title: str, csv_year: str, country: str, candidate: dict, cache_file: Path = CACHE_FILE) -> dict:
    """Kullanicinin elle sectigi eslesmeyi cache'e yazar, 'kontrol onerilir' bayragini kaldirir."""
    entry = cache.setdefault(uri, {"title": csv_title, "year": csv_year, "by_country": {}})
    entry["by_country"][country] = {
        "matched_title": candidate.get("matched_title"),
        "matched_year": candidate.get("matched_year"),
        "poster": candidate.get("poster"),
        "offers": candidate.get("offers", []),
        "platforms": candidate.get("platforms", []),
        "matched": True,
        "needs_review": False,
        "manually_confirmed": True,
    }
    save_cache(cache, cache_file)
    return entry["by_country"][country]


def sync_cache(
    rows: list[dict],
    cache: dict,
    country: str,
    language: str,
    cache_file: Path = CACHE_FILE,
    progress=None,
) -> tuple[dict, list[dict]]:
    """progress: opsiyonel callback(done, total, title) - her yeni/guncellenen film sonrasi cagirilir."""
    current_uris = {row["uri"] for row in rows}
    todo_rows = [row for row in rows if needs_lookup(cache, row["uri"], country)]
    errors = []

    for i, row in enumerate(todo_rows, 1):
        result, error = search_movie(row["title"], row["year"], country, language)
        if result is not None:
            entry = cache.setdefault(row["uri"], {"title": row["title"], "year": row["year"], "by_country": {}})
            entry["by_country"][country] = result
        else:
            errors.append({"title": row["title"], "year": row["year"], "uri": row["uri"], "error": error})
        if progress:
            progress(i, len(todo_rows), row["title"])
        time.sleep(REQUEST_DELAY_SECONDS)

    removed = [
        {"uri": uri, "title": data.get("title"), "year": data.get("year")}
        for uri, data in cache.items()
        if uri not in current_uris
    ]

    save_cache(cache, cache_file)
    return {"removed": removed, "current_uris": current_uris}, errors


def build_plan(cache: dict, current_uris: set, country: str, owned_platforms: list[str] | None = None) -> dict:
    owned = set(owned_platforms or [])
    films_by_platform: dict[str, set] = {}
    nowhere = []
    already_available = []

    def country_data(uri: str) -> dict | None:
        entry = cache.get(uri)
        if entry is None:
            return None
        return entry.get("by_country", {}).get(country)

    for uri in current_uris:
        data = country_data(uri)
        if data is None or not data.get("matched"):
            continue
        platforms = data.get("platforms") or []
        if not platforms:
            nowhere.append(uri)
            continue
        for platform in platforms:
            films_by_platform.setdefault(platform, set()).add(uri)
        if owned & set(platforms):
            already_available.append(uri)

    uncovered = set()
    for uris in films_by_platform.values():
        uncovered |= uris
    uncovered -= set(already_available)

    def movie_info(uri: str) -> dict:
        entry = cache[uri]
        data = country_data(uri) or {}
        needs_review = data.get("needs_review")
        if needs_review is None:
            # Eski cache kaydi (ozellik eklenmeden once aranmis) - yeniden
            # istek atmadan, zaten sakli matched_year ile geriye donuk hesapla.
            target_year = _target_year(entry.get("year"))
            needs_review = target_year is None or data.get("matched_year") != target_year
        return {
            "title": entry["title"],
            "year": entry["year"],
            "uri": uri,
            "poster": data.get("poster"),
            "offers": data.get("offers", []),
            "matched_title": data.get("matched_title"),
            "matched_year": data.get("matched_year"),
            "needs_review": bool(needs_review) and not data.get("manually_confirmed"),
        }

    monthly_plan = []
    month = 1
    while uncovered:
        best_platform = max(films_by_platform, key=lambda p: len(films_by_platform[p] & uncovered))
        covered = films_by_platform[best_platform] & uncovered
        if not covered:
            break
        movies = [movie_info(uri) for uri in covered]
        movies.sort(key=lambda m: m["title"])
        monthly_plan.append({"month": month, "platform": best_platform, "movies": movies})
        uncovered -= covered
        month += 1

    nowhere_movies = [movie_info(uri) for uri in nowhere]
    nowhere_movies.sort(key=lambda m: m["title"])

    already_available_movies = [movie_info(uri) for uri in already_available]
    already_available_movies.sort(key=lambda m: m["title"])

    # Platform basina TUM filmler (aylik plana hangi filmin atandigindan bagimsiz) -
    # "bu platforma zaten abonesem, watchlistimden neler izleyebilirim" sorusuna cevap.
    platforms_sorted = sorted(films_by_platform, key=lambda p: len(films_by_platform[p]), reverse=True)
    movies_by_platform = {}
    for platform in platforms_sorted:
        movies = [movie_info(uri) for uri in films_by_platform[platform]]
        movies.sort(key=lambda m: m["title"])
        movies_by_platform[platform] = movies

    return {
        "monthly_plan": monthly_plan,
        "not_available_anywhere": nowhere_movies,
        "already_available": already_available_movies,
        "movies_by_platform": movies_by_platform,
        "owned_platforms": sorted(owned),
    }


def process(
    csv_text: str,
    country: str = DEFAULT_COUNTRY,
    cache_file: Path = CACHE_FILE,
    progress=None,
    owned_platforms: list[str] | None = None,
) -> dict:
    """Tam pipeline: CSV metni -> plan. sync.py ve server.py bunu kullanir."""
    if country not in COUNTRIES:
        raise ValueError(f"Desteklenmeyen ulke kodu: {country}")
    language = language_for(country)

    rows = parse_csv_text(csv_text)
    cache = load_cache(cache_file)
    sync_info, errors = sync_cache(rows, cache, country, language, cache_file, progress=progress)
    plan = build_plan(cache, sync_info["current_uris"], country, owned_platforms=owned_platforms)
    plan["errors"] = errors
    plan["removed_from_watchlist"] = sync_info["removed"]
    plan["total_movies"] = len(rows)
    plan["country"] = country
    return plan
