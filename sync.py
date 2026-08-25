#!/usr/bin/env python
"""Letterboxd watchlist'ini JustWatch ile eslestirip hangi ay hangi
platforma abone olunacagini hesaplayan CLI script.

Kullanim:
    python sync.py [csv_dosyasi] [--country TR]

csv_dosyasi verilmezse, klasordeki "watchlist-*.csv" pattern'ine uyan
ilk dosya kullanilir. --country verilmezse TR kullanilir.

Gorsel, surukle-birak arayuz icin bkz: server.py
"""

import argparse
import glob
import json
import sys
from pathlib import Path

import core

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

PLAN_FILE = Path("plan.json")


def find_default_csv() -> str:
    matches = sorted(glob.glob("watchlist-*.csv"))
    if not matches:
        print("Hata: watchlist-*.csv bulunamadi. CSV dosyasini argument olarak ver.")
        sys.exit(1)
    return matches[0]


def print_report(plan: dict) -> None:
    country_name = core.COUNTRIES.get(plan["country"], (plan["country"],))[0]
    print("\n" + "=" * 60)
    print(f"AYLIK ABONELIK PLANI ({country_name} / {plan['country']})")
    print("=" * 60)
    total_movies = 0
    for step in plan["monthly_plan"]:
        print(f"\nAy {step['month']}: {step['platform']} ({len(step['movies'])} film)")
        for movie in step["movies"]:
            print(f"    - {movie['title']} ({movie['year']})")
        total_movies += len(step["movies"])

    print(f"\nToplam {len(plan['monthly_plan'])} ay ile {total_movies} film izlenebilir.")

    if plan["already_available"]:
        print(f"\nZaten sahip oldugun platformlarda izleyebilirsin - {', '.join(plan['owned_platforms'])} ({len(plan['already_available'])} film):")
        for movie in plan["already_available"]:
            print(f"    - {movie['title']} ({movie['year']})")

    if plan["not_available_anywhere"]:
        print(f"\nHicbir platformda abonelikle bulunamadi ({len(plan['not_available_anywhere'])} film):")
        for movie in plan["not_available_anywhere"]:
            print(f"    - {movie['title']} ({movie['year']})")

    if plan["removed_from_watchlist"]:
        print(f"\nWatchlist'ten cikmis ama cache'te olan filmler ({len(plan['removed_from_watchlist'])}):")
        for movie in plan["removed_from_watchlist"]:
            print(f"    - {movie['title']} ({movie['year']})")

    if plan["errors"]:
        print(f"\nSORUNLU FILMLER ({len(plan['errors'])}) - eslestirilemedi:")
        for err in plan["errors"]:
            print(f"    - {err['title']} ({err['year']}): {err['error']}")

    all_movies = [m for step in plan["monthly_plan"] for m in step["movies"]]
    all_movies += plan["already_available"] + plan["not_available_anywhere"]
    needs_review = [m for m in all_movies if m.get("needs_review")]
    if needs_review:
        print(f"\nESLESME KONTROLU ONERILIR ({len(needs_review)} film) - yil uyusmadi, yanlis film olabilir:")
        for movie in needs_review:
            print(f"    - {movie['title']} ({movie['year']}) -> JustWatch: {movie['matched_title']} ({movie['matched_year']})")
        print("    Duzeltmek icin gorsel arayuzu (server.py) kullan.")

    print()


def cli_progress(done: int, total: int, title: str) -> None:
    print(f"  [{done}/{total}] {title}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watchlist -> abonelik plani")
    parser.add_argument("csv_path", nargs="?", help="Letterboxd watchlist CSV dosyasi")
    parser.add_argument(
        "--country",
        default=core.DEFAULT_COUNTRY,
        help=f"Ulke kodu (varsayilan: {core.DEFAULT_COUNTRY}). Secenekler: {', '.join(core.COUNTRIES)}",
    )
    parser.add_argument(
        "--owned",
        default="",
        help="Zaten sahip oldugun platformlar, virgulle ayrilmis (orn. 'Netflix,Disney Plus'). "
        "Bu platformlardaki filmler ucretsiz sayilir, aylik plan geri kalanina gore kurulur.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    country = args.country.upper()
    if country not in core.COUNTRIES:
        print(f"Hata: bilinmeyen ulke kodu '{country}'. Secenekler: {', '.join(core.COUNTRIES)}")
        sys.exit(1)

    csv_path = args.csv_path if args.csv_path else find_default_csv()
    print(f"CSV okunuyor: {csv_path}")
    csv_text = Path(csv_path).read_text(encoding="utf-8")

    owned_platforms = [p.strip() for p in args.owned.split(",") if p.strip()]
    plan = core.process(csv_text, country=country, progress=cli_progress, owned_platforms=owned_platforms)

    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2, sort_keys=True)

    print_report(plan)
    print(f"Plan kaydedildi: {PLAN_FILE}")
    print(f"Cache kaydedildi: {core.CACHE_FILE}")


if __name__ == "__main__":
    main()
