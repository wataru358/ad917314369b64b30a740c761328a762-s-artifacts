"""内閣府の原本を保存し、4日間の日程に祝日・土日を付ける。

初回: .venv/bin/python build_trip_calendar.py --download
再現: .venv/bin/python build_trip_calendar.py （保存した原本のみ使用）
祝日を混雑の実測値や減点に変換しない。
"""

import argparse
import csv
import hashlib
import io
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.request import urlopen

BASE = Path(__file__).resolve().parent
RAW = BASE / "data/calendar"
OUT = BASE / "publication"
URL = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"
PAGE = "https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html"


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_holidays(raw):
    reader = csv.reader(io.StringIO(raw.decode("cp932")))
    if next(reader) != ["国民の祝日・休日月日", "国民の祝日・休日名称"]:
        raise ValueError("内閣府CSVの見出しが変わっています")
    holidays = {}
    for row in reader:
        if len(row) != 2 or not row[1].strip():
            raise ValueError(f"祝日行が不正: {row}")
        day = date(*map(int, row[0].split("/")))
        if day in holidays:
            raise ValueError(f"祝日が重複: {day}")
        holidays[day] = row[1]
    if min(holidays).year != 1955 or max(holidays).year < 2027:
        raise ValueError("想定した1955〜2027年が含まれていません")
    for year in range(2016, 2028):
        if not 16 <= sum(d.year == year for d in holidays) <= 22:
            raise ValueError(f"祝日数の要確認: {year}")
    return holidays


def trip_rows(first, last_start, holidays):
    rows = []
    for i in range((last_start - first).days + 1):
        start = first + timedelta(days=i)
        days = [start + timedelta(days=j) for j in range(4)]
        holiday_days = [d for d in days if d in holidays]
        rows.append({
            "start_date": start.isoformat(), "end_date": days[-1].isoformat(),
            "start_month": start.month,
            "holiday_days": len(holiday_days),
            "weekend_days": sum(d.weekday() >= 5 for d in days),
            # 土日と祝日が重なる日を二重に数えない。
            "weekend_or_holiday_days": sum(d.weekday() >= 5 or d in holidays for d in days),
            "holiday_dates": "|".join(d.isoformat() for d in holiday_days),
            "holiday_names": "|".join(holidays[d] for d in holiday_days),
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    source = RAW / "syukujitsu.csv"
    manifest = RAW / "source.json"
    if args.download:
        with urlopen(URL, timeout=45) as response:
            raw = response.read()
            headers = dict(response.headers)
        holidays = read_holidays(raw)  # 不正なレスポンスで原本を上書きしない。
        source.write_bytes(raw)
        manifest.write_text(json.dumps({
            "url": URL, "page_url": PAGE,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "sha256": hashlib.sha256(raw).hexdigest(), "encoding": "cp932",
            "first_holiday": str(min(holidays)), "last_holiday": str(max(holidays)),
            "coverage_through": "2027-12-31",
            "coverage_basis": "Official page lists calendar years 1955–2027",
            "response_headers": headers,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raw = source.read_bytes()
    metadata = json.loads(manifest.read_text())
    if hashlib.sha256(raw).hexdigest() != metadata["sha256"]:
        raise ValueError("保存原本と出典ハッシュが一致しません")
    holidays = read_holidays(raw)
    write_csv(OUT / "holidays_2016_2027.csv", [
        {"date": str(d), "name": name, "source_url": URL, "source_sha256": metadata["sha256"]}
        for d, name in sorted(holidays.items()) if 2016 <= d.year <= 2027
    ])
    # 気象側と同じ3,650開始日。2025年12月29〜31日は除く。
    historical = trip_rows(date(2016, 1, 1), date(2025, 12, 28), holidays)
    write_csv(OUT / "trip_calendar_2016_2025.csv", historical)
    monthly = []
    for month in range(1, 13):
        trips = [r for r in historical if r["start_month"] == month]
        monthly.append({
            "start_month": month, "candidate_trips": len(trips),
            "trips_with_holiday": sum(r["holiday_days"] > 0 for r in trips),
            "trips_with_holiday_pct": 100 * sum(r["holiday_days"] > 0 for r in trips) / len(trips),
            "trips_with_weekend": sum(r["weekend_days"] > 0 for r in trips),
            "denominator": "all_candidate_trips_not_weather_valid_trips",
        })
    write_csv(OUT / "trip_calendar_monthly_2016_2025.csv", monthly)
    # 2028年の祝日は未収録。年末の3開始日を非祝日扱いしない。
    future = trip_rows(date(2026, 1, 1), date(2027, 12, 28), holidays)
    write_csv(OUT / "trip_calendar_2026_2027.csv", future)
    print(f"Calendar: {len(historical)} historical starts, {len(future)} dated planning starts; 12 monthly rows")


if __name__ == "__main__":
    main()
