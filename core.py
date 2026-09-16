"""Letterboxd watchlist'ini JustWatch ile eslestiren ve aylik abonelik
planini ureten paylasilan mantik.

Hem sync.py (CLI) hem de server.py (web arayuzu) bu modulu kullanir.
"""

import csv
import io
import json
import re
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from simplejustwatchapi.exceptions import JustWatchHttpError
from simplejustwatchapi.justwatch import details, popular, search

CACHE_FILE = Path("justwatch_cache.json")
DEFAULT_COUNTRY = "TR"
# DIKKAT: JustWatch'in arama API'si `count` parametresine gore SADECE sonuc
# sayisini degil, DONDURULEN SONUCLARIN KENDISINI de degistirebiliyor - bu
# deterministik ama beklenmedik bir davranis. Canli test edildi: bazi
# sorgularda count=5 ile dogru film sonuclarda HIC YOKKEN, count=6-10
# arasinda ayni sorgu icin 1. sirada cikiyor (ayni istek 5 kez tekrarlandi,
# hep ayni sekilde "kayboluyor" - rastgele degil). count=5 (eski deger)
# otomatik eslestirmede gercek, tespit edilebilir "bulunamadi" hatalarina
# yol aciyordu. 10, birden fazla sorguda guvenilir calistigi dogrulanan
# bir deger - kucuk bir sayi secmekten kacinilmali.
SEARCH_COUNT = 10
# Hedef ulkenin kendi dilinde arama basarisiz olursa (asagida aciklandigi
# gibi) filmi guvenilir sekilde tespit etmek icin kullanilan yedek
# ulke/dil. en/US, JustWatch'in en genis/en iyi indekslenmis katalogu -
# neredeyse her filmin orijinal/Ingilizce basligiyla dogru sonuc veriyor.
FALLBACK_SEARCH_COUNTRY = "US"
FALLBACK_SEARCH_LANGUAGE = "en"
# Bir cache kaydi kac gun sonra "eski" sayilip yeniden aransin - platform
# katalogu zamanla degisiyor (bir film Netflix'ten kalkabilir vs.), sonsuza
# kadar ayni cevabi vermek yanlis bilgi verir. 7 gun, guncellik ile JustWatch'a
# ek yuk arasinda kullanicinin sectigi denge noktasi.
CACHE_TTL_SECONDS = 7 * 24 * 60 * 60
# JustWatch'ta hic sonuc bulunamayan (var olmayan/cok obskur) basliklar icin
# ayri, daha kisa bir TTL - bunlari da cache'lemezsek her senkronizasyonda
# ayni "bulunamadi" cevabini almak icin tekrar istek atariz. Pozitif eslesme
# TTL'inden kisa tutuluyor cunku JustWatch katalogu genisleyebilir (bugun
# olmayan bir film yarin eklenebilir), pozitif bir eslesmeye gore daha sik
# yeniden denenmesi mantikli.
NEGATIVE_CACHE_TTL_SECONDS = 3 * 24 * 60 * 60
# Tam yil eslesmesi bulunamadiginda, en yakin sonucu kabul etmek icin
# izin verilen maksimum yil farki. JustWatch bazi ulkelerde/kataloglarda
# festival ya da yerel vizyon tarihini "release year" olarak gosterebiliyor,
# bu da gercekte ayni film icin 1 yillik bir kaymaya yol acabiliyor - bunu
# tolere ediyoruz. Daha buyuk bir fark, JustWatch'in aramaya alakasiz bir
# sonuc dondurdugunun (baska bir film) isaretidir.
YEAR_TOLERANCE = 1
# Ayni anda JustWatch'a atilacak istek sayisi icin baslangic degeri. Ag
# gecikmesi tek tek istekleri yavaslatiyordu, bu da darbogazdi (CPU degil).
# Gercek limit artik sabit degil - asagidaki _AdaptiveLimiter (AIMD) bu
# baslangictan itibaren JustWatch'in tepkisine gore kendi kendine ayarlanir
# (bkz. asagisi). (500+ filmlik buyuk presetleri test ederken IP'nin gecici
# olarak 403 ile bloklandigi gozlemlenmisti - sabit deger yerine adaptif
# limit hem bu riske hizli tepki verir hem de sorun yoksa elle mudahale
# gerekmeden hizlanir.)
INITIAL_CONCURRENT_REQUESTS = 4
MIN_CONCURRENT_REQUESTS = 1
MAX_CONCURRENT_REQUESTS = 8
# Limit'i 1 arttirmadan once (additive increase) art arda kac basarili
# cagri gormemiz gerektigi. Cok kucuk olursa gurultuye (tek seferlik ag
# hatalarina) asiri tepki verip gereksiz yere hizlanip yavaslar dururuz;
# cok buyuk olursa guvenli oldugunda bile hizlanmamiz cok uzun surer.
_SUCCESSES_PER_INCREASE = 15

# Faz 3: her film icin ayri ayri search() atmak yerine, JustWatch'in "popular"
# (en cok bilinen/populer) kataloğunu birkac istekle topluca cekip yerel bir
# index'e cikariyoruz - watchlist'teki cogu film zaten mainstream oldugu icin
# bu index'te bulunur ve hic ag istegi gerekmeden aninda eslesir. Index
# ulke basina paylasilir (tum kullanicilar/senkronizasyonlar ayni kopyayi
# kullanir), obskur/az bilinen filmler icin yine eski tek-tek search() yoluna
# dusulur - index sadece bir hizlandirma katmani, tek dogruluk kaynagi degil.
#
# JustWatch'in GraphQL API'si count=250+ istendiginde "page too large" hatasi
# veriyor (canli test edildi) - 100, hata vermeden calistigi dogrulanan guvenli
# bir sayfa boyutu. API'nin kendisi de offset+count >= 2000 oldugunda bos liste
# donduruyor (bkz. simplejustwatchapi popular() docstring'i) - yani katalogun
# tamami degil, en populer ~2000 baslik.
POPULAR_PAGE_SIZE = 100
POPULAR_MAX_OFFSET = 1999
# Populer film siralamasi/kataloğu her gun degismez - 1 gunluk TTL, tazelik
# ile JustWatch'a (ve Redis/disk yazma) ek yuk arasinda makul bir denge.
POPULAR_INDEX_TTL_SECONDS = 24 * 60 * 60

# JustWatch'in engelleme/rate-limit'i HTTP durum kodu olarak bildirdigi
# vakalar (429 Too Many Requests, 403 Forbidden, 503 Service Unavailable).
# Bunlari, GraphQL'in gecerli ama "sonuc yok" turu hatalarindan (orn. gecersiz
# node ID) ayirt etmemiz lazim - sadece bunlar gercek bir "yavasla" isaretidir.
_BLOCK_STATUS_RE = re.compile(r"\b(429|403|503)\b")


def _looks_like_block(exc: Exception) -> bool:
    return bool(_BLOCK_STATUS_RE.search(str(exc)))


class _AdaptiveLimiter:
    """Calisirken buyuklugu degistirilebilen bir concurrency limiti (AIMD).

    threading.Semaphore'un aksine limit sabit degil: art arda basarili
    cagrilardan sonra yavas yavas artar (additive increase), bir engelleme
    isareti (429/403/503) gorulur gorulmez aninda yariya iner (multiplicative
    decrease). Boylece "kac istek guvenli" sorusunun cevabini elle sabit bir
    sayi secmek yerine calisirken kendimiz ogreniriz.
    """

    def __init__(self, initial: int, minimum: int, maximum: int, successes_per_increase: int):
        self._limit = initial
        self._min = minimum
        self._max = maximum
        self._successes_per_increase = successes_per_increase
        self._active = 0
        self._success_streak = 0
        self._cond = threading.Condition()

    def acquire(self) -> None:
        with self._cond:
            while self._active >= self._limit:
                self._cond.wait()
            self._active += 1

    def release(self) -> None:
        with self._cond:
            self._active -= 1
            self._cond.notify()

    def report(self, blocked: bool) -> None:
        with self._cond:
            if blocked:
                self._success_streak = 0
                new_limit = max(self._min, self._limit // 2)
                if new_limit != self._limit:
                    self._limit = new_limit
                    self._cond.notify_all()
            else:
                self._success_streak += 1
                if self._success_streak >= self._successes_per_increase and self._limit < self._max:
                    self._success_streak = 0
                    self._limit += 1
                    self._cond.notify_all()

    @property
    def current_limit(self) -> int:
        with self._cond:
            return self._limit


_ADAPTIVE_LIMITER = _AdaptiveLimiter(
    initial=INITIAL_CONCURRENT_REQUESTS,
    minimum=MIN_CONCURRENT_REQUESTS,
    maximum=MAX_CONCURRENT_REQUESTS,
    successes_per_increase=_SUCCESSES_PER_INCREASE,
)


def _call_justwatch(fn, *args, **kwargs):
    """search()/details() cagrilarini adaptif limiter'dan (yukarida) gecirir;
    sonucu (basari/blok) limiter'a bildirip limitin buyumesine/kuculmesine
    sebep olur. search_movie/search_candidates icindeki her JustWatch agi
    cagrisi bunun uzerinden yapilir."""
    _ADAPTIVE_LIMITER.acquire()
    try:
        result = fn(*args, **kwargs)
    except JustWatchHttpError as exc:
        _ADAPTIVE_LIMITER.report(blocked=_looks_like_block(exc))
        raise
    except Exception:
        _ADAPTIVE_LIMITER.report(blocked=False)
        raise
    else:
        _ADAPTIVE_LIMITER.report(blocked=False)
        return result
    finally:
        _ADAPTIVE_LIMITER.release()

# Single-flight: birden fazla kullanici ayni anda ayni (baslik, yil, ulke, dil)
# icin arama tetiklerse (ayri sync_cache cagrilari - farkli yukleme isleri),
# JustWatch'a sadece bir istek gitsin, digerleri o istegin sonucunu beklesin.
# Semaphore sadece "ayni anda kac istek" sinirini koyar, ayni sorguyu birden
# fazla kez atmayi engellemez - bu onu engeller.


class _InflightSlot:
    __slots__ = ("event", "result")

    def __init__(self):
        self.event = threading.Event()
        self.result = None


_INFLIGHT: dict[tuple, "_InflightSlot"] = {}
_INFLIGHT_GUARD = threading.Lock()


def _singleflight_search_movie(
    title: str, year: str, country: str, language: str, popular_index: dict | None = None
) -> tuple[dict | None, str | None]:
    key = (title, year, country, language)
    with _INFLIGHT_GUARD:
        slot = _INFLIGHT.get(key)
        if slot is None:
            slot = _InflightSlot()
            _INFLIGHT[key] = slot
            is_leader = True
        else:
            is_leader = False

    if not is_leader:
        slot.event.wait()
        return slot.result

    try:
        slot.result = search_movie(title, year, country, language, popular_index=popular_index)
    finally:
        with _INFLIGHT_GUARD:
            del _INFLIGHT[key]
        slot.event.set()
    return slot.result


# Desteklenen ulkeler: kod -> {goruntulenen isim (tr/en), JustWatch dil kodu}.
# Ulke isimleri arayuz dili tr/en icin ayri ayri tutulur; yeni bir arayuz dili
# eklendiginde her ulkeye o dilde bir isim eklemek yeterli.
COUNTRIES = {
    "TR": {"tr": "Türkiye", "en": "Turkey", "lang": "tr"},
    "US": {"tr": "Amerika Birleşik Devletleri", "en": "United States", "lang": "en"},
    "GB": {"tr": "İngiltere", "en": "United Kingdom", "lang": "en"},
    "DE": {"tr": "Almanya", "en": "Germany", "lang": "de"},
    "FR": {"tr": "Fransa", "en": "France", "lang": "fr"},
    "ES": {"tr": "İspanya", "en": "Spain", "lang": "es"},
    "IT": {"tr": "İtalya", "en": "Italy", "lang": "it"},
    "NL": {"tr": "Hollanda", "en": "Netherlands", "lang": "nl"},
    "PT": {"tr": "Portekiz", "en": "Portugal", "lang": "pt"},
    "BR": {"tr": "Brezilya", "en": "Brazil", "lang": "pt"},
    "CA": {"tr": "Kanada", "en": "Canada", "lang": "en"},
    "AU": {"tr": "Avustralya", "en": "Australia", "lang": "en"},
    "MX": {"tr": "Meksika", "en": "Mexico", "lang": "es"},
    "PL": {"tr": "Polonya", "en": "Poland", "lang": "pl"},
    "SE": {"tr": "İsveç", "en": "Sweden", "lang": "sv"},
    "IN": {"tr": "Hindistan", "en": "India", "lang": "en"},
    "JP": {"tr": "Japonya", "en": "Japan", "lang": "ja"},
    "KR": {"tr": "Güney Kore", "en": "South Korea", "lang": "ko"},
    "RU": {"tr": "Rusya", "en": "Russia", "lang": "ru"},
    "AR": {"tr": "Arjantin", "en": "Argentina", "lang": "es"},
}


def language_for(country: str) -> str:
    return COUNTRIES.get(country, {}).get("lang", "en")


EXPECTED_CSV_COLUMNS = ["Date", "Name", "Year", "Letterboxd URI"]


def parse_csv_text(text: str) -> list[dict]:
    rows = []
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or not set(EXPECTED_CSV_COLUMNS) <= set(reader.fieldnames):
        raise ValueError(
            "Bu dosya beklenen Letterboxd watchlist formatında değil "
            f"(gerekli kolonlar: {', '.join(EXPECTED_CSV_COLUMNS)}). "
            "Letterboxd'dan Ayarlar -> Import & Export -> Export Data ile "
            "indirdiğin watchlist.csv dosyasını kullandığından emin ol."
        )
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


def apply_overrides(rows: list[dict], overrides: dict | None) -> list[dict]:
    """CSV'den bagimsiz elle eklenen/cikarilan filmleri satirlara uygular.

    overrides: {"added": [{"uri", "title", "year"}, ...], "removed": [uri, ...]}
    Boylece kullanici Letterboxd'dan tekrar export almadan watchlist'ine
    film ekleyip cikarabilir - tercih sunucuda ayri bir dosyada saklanir ve
    her CSV yuklemesinde/yeniden acilista yeniden uygulanir.
    """
    if not overrides:
        return rows
    removed = set(overrides.get("removed", []))
    rows = [row for row in rows if row["uri"] not in removed]
    existing_uris = {row["uri"] for row in rows}
    for added in overrides.get("added", []):
        uri = added["uri"]
        if uri in removed or uri in existing_uris:
            continue
        rows.append({"date": "", "title": added["title"], "year": added["year"], "uri": uri})
        existing_uris.add(uri)
    return rows


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
    raw = json.loads(cache_file.read_text(encoding="utf-8"))
    return {uri: _migrate_entry(uri, entry) for uri, entry in raw.items()}


def save_cache(cache: dict, cache_file: Path = CACHE_FILE) -> None:
    cache_file.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )


_CACHE_LOCKS: dict[str, threading.Lock] = {}
_CACHE_LOCKS_GUARD = threading.Lock()


def _cache_lock(cache_file: Path) -> threading.Lock:
    key = str(cache_file)
    with _CACHE_LOCKS_GUARD:
        lock = _CACHE_LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _CACHE_LOCKS[key] = lock
        return lock


def _merge_and_save(cache_file: Path, new_entries: dict[str, dict]) -> None:
    """new_entries: {uri: full cache-entry dict}. Diskteki/Redis'teki en guncel
    kopyayi tekrar okuyup sadece bu is'in bulduklarini uzerine birlestirir ve
    kaydeder - ayni cache dosyasina ayni anda yazan baska bir istek (baska bir
    kullanicinin aramasi) uzerine yazilmasin diye kilitli, kisa omurlu bir
    islem. Aramalarin kendisi (yavas kisim) bu kilidin disinda kalir."""
    if not new_entries:
        return
    with _cache_lock(cache_file):
        fresh = load_cache(cache_file)
        for uri, entry in new_entries.items():
            target = fresh.setdefault(uri, {"title": entry.get("title"), "year": entry.get("year"), "by_country": {}})
            target["by_country"].update(entry.get("by_country", {}))
        save_cache(fresh, cache_file)


def flatrate_offers(entry) -> list[dict]:
    """Unique FLATRATE (abonelik) teklifleri, platform basina bir tane."""
    offers = []
    seen = set()
    for offer in entry.offers:
        name = offer.package.name
        if offer.monetization_type != "FLATRATE" or name in seen:
            continue
        seen.add(name)
        offers.append({"platform": name, "url": offer.url})
    return offers


def rent_buy_offers(entry) -> list[dict]:
    """Kirala/satin al teklifleri - platform + tur (RENT/BUY) basina en ucuz
    teklif (ayni platformda SD/HD/4K gibi birden fazla kalite secenegi
    olabilir, hepsini degil tek bir temsili fiyati gosteriyoruz)."""
    best: dict[tuple[str, str], dict] = {}
    for offer in entry.offers:
        if offer.monetization_type not in ("RENT", "BUY"):
            continue
        key = (offer.package.name, offer.monetization_type)
        current = best.get(key)
        cheaper = (
            current is None
            or (offer.price_value is not None and (current["price_value"] is None or offer.price_value < current["price_value"]))
        )
        if cheaper:
            best[key] = {
                "platform": offer.package.name,
                "type": offer.monetization_type,
                "price": offer.price_string,
                "price_value": offer.price_value,
                "url": offer.url,
            }
    return list(best.values())


def entry_to_candidate(entry) -> dict:
    """Bir JustWatch MediaEntry'sini cache/UI'da kullanilan sozluk formuna cevirir."""
    offers = flatrate_offers(entry)
    return {
        "matched_title": entry.title,
        "matched_year": entry.release_year,
        "poster": entry.poster,
        "offers": offers,
        "platforms": [o["platform"] for o in offers],
        "rent_buy_offers": rent_buy_offers(entry),
        "matched": True,
    }


def needs_lookup(cache: dict, uri: str, country: str) -> bool:
    entry = cache.get(uri)
    if entry is None:
        return True
    data = entry.get("by_country", {}).get(country)
    if data is None:
        return True
    if data.get("manually_confirmed"):
        # Kullanicinin elle duzelttigi eslesmeyi otomatik arama geri
        # cevirmesin (otomatik algoritma farkli bir filmi secebilir) -
        # bu kayitlar TTL'den bagimsiz gecerli sayilir.
        return False
    checked_at = data.get("checked_at")
    if checked_at is None:
        return True  # bu ozellik eklenmeden once aranmis eski kayit
    ttl = CACHE_TTL_SECONDS if data.get("matched") else NEGATIVE_CACHE_TTL_SECONDS
    return (time.time() - checked_at) > ttl


def _target_year(year: str) -> int | None:
    try:
        return int(year)
    except (TypeError, ValueError):
        return None


def _exact_year_entry(results: list, target_year: int):
    for entry in results:
        if entry.release_year == target_year:
            return entry
    return None


def _year_matched_entry(results: list, target_year: int):
    """results icinde target_year ile tam eslesen bir kayit varsa onu, yoksa
    (YEAR_TOLERANCE icinde kalan) en yakin yillisini, o da yoksa None doner.

    SADECE guvenilir/iyi indekslenmis bir katalogda (FALLBACK_SEARCH_COUNTRY,
    yani en/US) kullanilmali - bkz. search_movie. Hedef ulkenin kendi
    dilindeki aramada (TR gibi) bu tolerans TEHLIKELI: JustWatch'in fuzzy
    aramasi o kadar gevsek olabiliyor ki tamamen alakasiz bir film, sadece
    yil olarak 1 yakin oldugu icin kabul edilebiliyor (canli test edildi:
    'Loving Vincent' (2017) TR aramasinda, alakasiz bir film olan 'Sevmek'
    (2016) ile 1 yil farkla "yakin" sayilip yanlislikla eslesiyordu). Bu
    yuzden hedef ulke aramasinda SADECE _exact_year_entry kullanilir; tam
    eslesme yoksa dogrudan US/en fallback'e devredilir - tolerans SADECE
    orada, guvenilir katalogda uygulanir.

    Baslik metni burada kullanilmiyor: JustWatch sonucu hedef ulkenin dilinde
    dondurur (ceviri), bu yuzden metin benzerligi guvenilir bir sinyal degil -
    "Ice Age" vs "Buz Devri" gibi DOGRU bir eslesme bile dusuk metin
    benzerligi verebilir. Yil, ceviriden bagimsiz ve bir filmin gercekten
    ayni film olup olmadigini gosteren cok daha guvenilir bir isaret.
    """
    exact = _exact_year_entry(results, target_year)
    if exact is not None:
        return exact
    candidates_with_year = [e for e in results if e.release_year is not None]
    if not candidates_with_year:
        return None
    closest = min(candidates_with_year, key=lambda e: abs(e.release_year - target_year))
    if abs(closest.release_year - target_year) <= YEAR_TOLERANCE:
        return closest
    return None


def _normalize_title_key(title: str) -> str:
    """Populer index'te ve watchlist aramasinda ayni basligi ayni anahtara
    esler: kucuk harfe cevirir, aksan/ozel karakterleri sadelestirir
    (unicodedata ile), harf/rakam disindaki her seyi (bosluk, noktalama)
    atar. Sadece bir index anahtari - kullaniciya gosterilen baslik hep
    JustWatch'in kendi entry.title'indan gelir, bu fonksiyonun ciktisi degil.
    """
    decomposed = unicodedata.normalize("NFKD", title or "")
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]", "", ascii_only.lower())


def build_popular_index(country: str, language: str) -> dict[str, dict[str, dict]]:
    """JustWatch'in "popular" katalogunu POPULAR_PAGE_SIZE'lik sayfalar halinde
    tarayip {normalize_edilmis_baslik: {yil_str: candidate_dict}} seklinde
    yerel bir index'e cikarir. Sadece filmlerle (object_types=MOVIE)
    sinirlandirilir - watchlist'ler Letterboxd'dan geldigi icin hep film.

    popular(), search()'un aksine serbest metin araması yapmaz - JustWatch'in
    kendi katalog listesini dogrudan donduruyor, bu yuzden TR gibi ulkelerde
    bile (search()'te gordugumuz fuzzy/alakasiz sonuc riski olmadan) guvenle
    tam yil eslesmesi icin kullanilabilir.

    Bir sayfa cekilirken hata olursa (agi kesintisi vb.) o ana kadar
    toplananlarla index'i tamamlar - kismi bir index, hic index olmamasindan
    iyidir (kalan basliklar zaten eski, tek-tek search() yoluna duser).
    """
    index: dict[str, dict[str, dict]] = {}
    offset = 0
    while offset <= POPULAR_MAX_OFFSET:
        try:
            page = _call_justwatch(
                popular,
                country=country,
                language=language,
                count=POPULAR_PAGE_SIZE,
                offset=offset,
                object_types="MOVIE",
            )
        except Exception:
            break
        if not page:
            break
        for entry in page:
            if entry.release_year is None:
                continue
            year_bucket = index.setdefault(_normalize_title_key(entry.title), {})
            year_bucket.setdefault(str(entry.release_year), entry_to_candidate(entry))
        offset += POPULAR_PAGE_SIZE
    return index


def load_popular_index(cache_file: Path) -> dict | None:
    """Diskteki/Redis'teki populer index'i TTL icindeyse doner, degilse
    (yok/eski/bozuk) None doner - cagiran yeniden insa etmesi gerektigini
    boylece anlar."""
    if not cache_file.exists():
        return None
    try:
        raw = json.loads(cache_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return None
    built_at = raw.get("built_at")
    if built_at is None or (time.time() - built_at) > POPULAR_INDEX_TTL_SECONDS:
        return None
    return raw.get("index")


def save_popular_index(index: dict, cache_file: Path) -> None:
    cache_file.write_text(
        json.dumps({"built_at": time.time(), "index": index}, ensure_ascii=False),
        encoding="utf-8",
    )


def ensure_popular_index(country: str, language: str, cache_file: Path) -> dict:
    """TTL icinde taze bir populer index varsa onu doner, yoksa JustWatch'tan
    yeniden insa edip kaydeder. Insa etmek ~20 istek suruyor ama sonuc ulke
    basina paylasilir (tum kullanicilar/senkronizasyonlar), bu yuzden
    POPULAR_INDEX_TTL_SECONDS boyunca tekrar tekrar insa edilmez."""
    cached = load_popular_index(cache_file)
    if cached is not None:
        return cached
    index = build_popular_index(country, language)
    if index:
        save_popular_index(index, cache_file)
    return index


def _lookup_popular_index(index: dict, title: str, target_year: int | None) -> dict | None:
    """Index'te (baslik, tam yil) eslesmesi varsa candidate dict'inin bir
    kopyasini doner, yoksa None. Yil bilinmiyorsa (target_year is None)
    guvenli bir eslesme kriterimiz olmadigi icin index'e hic bakmiyoruz -
    cagiran eski (results[0]) davranisina duser."""
    if target_year is None or not index:
        return None
    year_bucket = index.get(_normalize_title_key(title))
    if not year_bucket:
        return None
    candidate = year_bucket.get(str(target_year))
    if candidate is None:
        return None
    return dict(candidate)


def _fallback_identify_and_fetch(title: str, target_year: int, country: str, language: str):
    """Hedef ulkenin kendi dilinde guvenilir bir eslesme bulunamadiginda
    (bkz. search_movie) cagrilir.

    JustWatch, aranan film o ulkede/kataloğunda hic mevcut olmadiginda bos
    sonuc donmek yerine alakasiz baslikler donduruyor (canli test edildi:
    'Das Boot' TR aramasinda anime/dizi sonuclari veriyor, ama US/en
    aramasinda ilk sirada birebir dogru cikiyor). Bu yuzden filmi once
    en genis/en iyi indekslenmis katalog olan en/US uzerinden guvenilir
    sekilde TESPIT ediyoruz, sonra o ID ile hedef ulkedeki GERCEK
    tekliflerini details() ile ayrica soruyoruz. Film gercekten hedef
    ulkede yoksa bu da bos bir teklif listesiyle doner - bu artik yanlis
    bir tahmin degil, dogru/onaylanmis bir "bu ulkede mevcut degil" sonucu.
    """
    try:
        fallback_results = _call_justwatch(
            search, title, country=FALLBACK_SEARCH_COUNTRY, language=FALLBACK_SEARCH_LANGUAGE, count=SEARCH_COUNT
        )
    except Exception:
        return None
    identified = _year_matched_entry(fallback_results, target_year)
    if identified is None:
        return None
    try:
        return _call_justwatch(details, identified.entry_id, country=country, language=language)
    except Exception:
        return None


def search_movie(
    title: str, year: str, country: str, language: str, popular_index: dict | None = None
) -> tuple[dict | None, str | None]:
    """Returns (by_country_entry_dict, error_message).

    Ag/istek hatalarinda (None, hata_mesaji) doner - bu cache'lenmez, bir
    sonraki senkronizasyonda tekrar denenir (gecici olabilir). JustWatch'ta
    hic guvenilir sonuc bulunamadiginda ise (None, hata) DEGIL, matched=False
    bir sozluk donuyoruz - bu, aramanin basarili ama negatif oldugunu
    isaretler ve cagiran tarafindan (sync_cache) NEGATIVE_CACHE_TTL_SECONDS
    ile cache'lenir, boylece ayni "yok" cevabi icin tekrar tekrar istek
    atilmaz.

    popular_index verilirse (bkz. ensure_popular_index - Faz 3), once orada
    tam yil eslesmesi aranir; bulunursa JustWatch'a hic ag istegi atilmadan
    aninda sonuc donulur. Bulunamazsa (obskur film, index'te yok) eskisi
    gibi canli search()'e dusulur - index sadece bir hizlandirma katmani.
    """
    target_year = _target_year(year)

    indexed = _lookup_popular_index(popular_index, title, target_year) if popular_index else None
    if indexed is not None:
        indexed["needs_review"] = False
        indexed["manually_confirmed"] = False
        indexed["checked_at"] = time.time()
        return indexed, None

    try:
        results = _call_justwatch(search, title, country=country, language=language, count=SEARCH_COUNT)
    except Exception as exc:  # network / rate limit / API errors
        return None, f"JustWatch istegi basarisiz: {exc}"

    if target_year is None:
        # CSV'de yil yoksa elimizde guvenilir bir filtre yok - eskisi gibi
        # ilk sonuca dusuyoruz, ama kontrol onerilir olarak isaretliyoruz.
        chosen = results[0] if results else None
    elif country == FALLBACK_SEARCH_COUNTRY:
        # Zaten en guvenilir/iyi indekslenmis katalogda ariyoruz (en/US) -
        # yakin yil toleransi burada guvenli, ayrica bir fallback'e gerek yok.
        chosen = _year_matched_entry(results, target_year) if results else None
    else:
        # Hedef ulkenin (TR gibi) kendi dilindeki aramasi bazen alakasiz/fuzzy
        # sonuclar donduruyor, bu yuzden SADECE tam yil eslesmesine
        # guveniyoruz (bkz. _year_matched_entry'nin docstring'i). Tam eslesme
        # yoksa, yakin-ama-tam-degil bir TR sonucunu riske atmak yerine daha
        # guvenilir olan US/en fallback'e devrediyoruz.
        chosen = _exact_year_entry(results, target_year) if results else None
        if chosen is None:
            chosen = _fallback_identify_and_fetch(title, target_year, country, language)

    if chosen is None:
        # Ne dogrudan ne de (varsa) yedek arama guvenilir bir sonuc verdi -
        # JustWatch'in dondurdugu sonuclarin aranan filmle alakasiz oldugu
        # anlamina gelir (ornek: "On the Silver Globe" (1988) aramasinin
        # "Doctor on the Edge" (2026) ile eslesmesi). Yanlis ama "eslesti"
        # gibi gorunen bir sonucu sessizce cache'lemek yerine "bulunamadi"
        # sayiyoruz - bu, negatif cache'e duser ve kullaniciya manuel
        # eslestirme secenegi olarak gosterilir.
        return {
            "matched": False,
            "needs_review": False,
            "manually_confirmed": False,
            "checked_at": time.time(),
        }, None

    # Yil eslesmediyse (ya da CSV'de yil yoksa) bu, tam eslesmeye
    # dusulmedigi anlamina gelir - remake/ayni isimli baska film riski var,
    # kontrol onerilir.
    needs_review = target_year is None or chosen.release_year != target_year

    candidate = entry_to_candidate(chosen)
    candidate["needs_review"] = needs_review
    candidate["manually_confirmed"] = False
    candidate["checked_at"] = time.time()
    return candidate, None


def search_candidates(
    title: str, country: str, language: str, count: int = 8, target_year: str | None = None
) -> tuple[list[dict], str | None]:
    """Rematch/duzeltme arayuzu icin butun aday sonuclari dondurur (otomatik secim yapmaz).

    search_movie() gibi bu da hedef ulkenin (TR gibi) dogrudan aramasinin
    alakasiz sonuclar dondurebilecegi durumlar icin US/en katalogundan da
    aday topluyor - aksi halde kullanici manuel duzeltme yapmak istedigi
    bir filmi (ornek: 'Mad God') bizim arama kutumuzda hic bulamiyor, ustelik
    otomatik eslestirme onu zaten dogru bulmus olsa bile (bkz. search_movie).
    Bu fonksiyon TEK bir baslik icin, kullanicinin kendi istegiyle
    tetiklenen bir arama oldugu icin (toplu is degil), ekstra istek maliyeti
    kabul edilebilir.

    target_year verilirse (rematch akisinda watchlist'teki filmin yili hep
    biliniyor), liste yila yakinliga gore siralanir - aksi halde TR sonuclari
    hep once, US fallback sonuclari hep sonra geliyor, bu da TR'nin alakasiz
    dondugu durumlarda (bkz. 'On the Silver Globe') dogru cevabi listenin
    ortasina/sonuna gomup kullanicinin "sistem bunu bulamiyor" sanmasina yol
    aciyor - oysa dogru cevap genelde US/en'de 1. sirada, sadece TR'nin
    onune eklendigi sonuclar yuzunden gorunmez oluyor.
    """
    try:
        direct_results = _call_justwatch(search, title, country=country, language=language, count=count)
    except Exception as exc:
        return [], f"JustWatch istegi basarisiz: {exc}"

    candidates = [entry_to_candidate(entry) for entry in direct_results]
    seen_ids = {entry.entry_id for entry in direct_results}

    if country != FALLBACK_SEARCH_COUNTRY:
        try:
            fallback_results = _call_justwatch(
                search, title, country=FALLBACK_SEARCH_COUNTRY, language=FALLBACK_SEARCH_LANGUAGE, count=count
            )
        except Exception:
            fallback_results = []
        for entry in fallback_results:
            if entry.entry_id in seen_ids:
                continue
            seen_ids.add(entry.entry_id)
            try:
                detailed = _call_justwatch(details, entry.entry_id, country=country, language=language)
            except Exception:
                continue
            candidates.append(entry_to_candidate(detailed))

    if not candidates:
        return [], "JustWatch'ta sonuc bulunamadi"

    year_int = _target_year(target_year) if target_year else None
    if year_int is not None:
        def year_distance(candidate: dict) -> int:
            matched_year = candidate.get("matched_year")
            if matched_year is None:
                return 9999
            return abs(matched_year - year_int)

        candidates.sort(key=year_distance)

    return candidates, None


def confirm_match(cache: dict, uri: str, csv_title: str, csv_year: str, country: str, candidate: dict, cache_file: Path = CACHE_FILE) -> dict:
    """Kullanicinin elle sectigi eslesmeyi cache'e yazar, 'kontrol onerilir' bayragini kaldirir."""
    entry = cache.setdefault(uri, {"title": csv_title, "year": csv_year, "by_country": {}})
    entry["by_country"][country] = {
        "matched_title": candidate.get("matched_title"),
        "matched_year": candidate.get("matched_year"),
        "poster": candidate.get("poster"),
        "offers": candidate.get("offers", []),
        "platforms": candidate.get("platforms", []),
        "rent_buy_offers": candidate.get("rent_buy_offers", []),
        "matched": True,
        "needs_review": False,
        "manually_confirmed": True,
        "checked_at": time.time(),
    }
    _merge_and_save(cache_file, {uri: entry})
    return entry["by_country"][country]


def sync_cache(
    rows: list[dict],
    cache: dict,
    country: str,
    language: str,
    cache_file: Path = CACHE_FILE,
    progress=None,
    popular_index_file: Path | None = None,
) -> tuple[dict, list[dict]]:
    """progress: opsiyonel callback(done, total, title) - her yeni/guncellenen film sonrasi cagirilir.

    Aramalar en fazla MAX_CONCURRENT_REQUESTS (8) thread'de paralel yapilir
    (ag gecikmesi darbogaz oldugu icin, CPU degil) - ama gercekte ayni anda
    JustWatch'a giden istek sayisini _AdaptiveLimiter (AIMD) belirler:
    INITIAL_CONCURRENT_REQUESTS (4) ile baslar, sorun yoksa yavasca bu
    havuz boyutuna kadar hizlanir, bir blok isareti gorunce hemen yarisina
    iner. Ayni (baslik, yil) icin watchlist'te birden fazla satir varsa tek
    arama yapilir, sonuc hepsine uygulanir. Cache'e yazma ve hata biriktirme
    sadece ana thread'de olur, bu yuzden kilit gerekmiyor - sadece ilerleme
    sayaci paylasildigi icin kilitli.

    popular_index_file verilmezse ulkeye ozel bir varsayilan kullanilir
    (bkz. ensure_popular_index - Faz 3). Aranacak film yoksa (todo_rows bos)
    index hic yuklenmez/insa edilmez - bosuna is yapilmaz.
    """
    current_uris = {row["uri"] for row in rows}
    todo_rows = [row for row in rows if needs_lookup(cache, row["uri"], country)]
    errors = []

    queries: dict[tuple[str, str], list[dict]] = {}
    for row in todo_rows:
        queries.setdefault((row["title"], row["year"]), []).append(row)

    popular_index: dict = {}
    if queries:
        if popular_index_file is None:
            popular_index_file = Path(f"justwatch_popular_index_{country}.json")
        try:
            popular_index = ensure_popular_index(country, language, popular_index_file)
        except Exception:
            # Populer index isteğe bagli bir hizlandirma - insa edilemezse
            # (ornek: JustWatch tamamen erisilemez) tum senkronizasyonu
            # bloklamak yerine eski tek-tek search() yoluna dususuruz.
            popular_index = {}

    total = len(queries)
    done_count = 0
    progress_lock = threading.Lock()

    def run_one(key: tuple[str, str]):
        title, year = key
        result, error = _singleflight_search_movie(title, year, country, language, popular_index)
        nonlocal done_count
        with progress_lock:
            done_count += 1
            if progress:
                progress(done_count, total, title)
        return key, result, error

    new_entries: dict[str, dict] = {}

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
        futures = [executor.submit(run_one, key) for key in queries]
        for future in as_completed(futures):
            key, result, error = future.result()
            for row in queries[key]:
                if result is not None:
                    entry = cache.setdefault(row["uri"], {"title": row["title"], "year": row["year"], "by_country": {}})
                    entry["by_country"][country] = dict(result)
                    new_entries.setdefault(
                        row["uri"], {"title": row["title"], "year": row["year"], "by_country": {}}
                    )["by_country"][country] = dict(result)
                else:
                    errors.append({"title": row["title"], "year": row["year"], "uri": row["uri"], "error": error})

    # Negatif cache'lenmis (bu turda arandi ya da onceki bir turdan kalma,
    # TTL'i henuz dolmadigi icin bu turda hic aranmayan) satirlari da
    # "eslestirilemedi" listesine ekle - yoksa kullanici bunlari sadece ilk
    # bulunamadiginda gorur, sonraki (cache'ten gecen) senkronizasyonlarda
    # sessizce plandan kaybolurlar.
    already_errored = {e["uri"] for e in errors}
    for row in rows:
        if row["uri"] in already_errored:
            continue
        data = cache.get(row["uri"], {}).get("by_country", {}).get(country)
        if data is not None and data.get("matched") is False:
            errors.append(
                {"title": row["title"], "year": row["year"], "uri": row["uri"], "error": "JustWatch'ta sonuc bulunamadi"}
            )

    removed = [
        {"uri": uri, "title": data.get("title"), "year": data.get("year")}
        for uri, data in cache.items()
        if uri not in current_uris
    ]

    _merge_and_save(cache_file, new_entries)
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
            "rent_buy_offers": data.get("rent_buy_offers", []),
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
    overrides: dict | None = None,
    popular_index_file: Path | None = None,
) -> dict:
    """Tam pipeline: CSV metni -> plan. sync.py ve server.py bunu kullanir."""
    if country not in COUNTRIES:
        raise ValueError(f"Desteklenmeyen ulke kodu: {country}")
    language = language_for(country)

    rows = parse_csv_text(csv_text)
    rows = apply_overrides(rows, overrides)
    cache = load_cache(cache_file)
    sync_info, errors = sync_cache(
        rows, cache, country, language, cache_file, progress=progress, popular_index_file=popular_index_file
    )
    plan = build_plan(cache, sync_info["current_uris"], country, owned_platforms=owned_platforms)
    plan["errors"] = errors
    plan["removed_from_watchlist"] = sync_info["removed"]
    plan["total_movies"] = len(rows)
    plan["country"] = country
    return plan
