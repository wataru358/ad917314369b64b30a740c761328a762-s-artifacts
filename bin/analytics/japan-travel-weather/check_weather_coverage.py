"""JMA日別CSVの最高気温・降水量を検査する（標準ライブラリのみ）。

uv run python check_weather_coverage.py --list-stations
uv run python check_weather_coverage.py

原本のCP932、変換済みUTF-8のどちらも読める。同名の_utf8版は内容一致を確認して除外する。
対応表の履歴判定は保持し、日別検査の結果を別ファイルに保存する。
"""

import argparse  # 入出力フォルダなどをコマンドラインから指定する。
import csv  # CSVの引用符やカンマを正しく扱う。
import hashlib  # 検査した原本の内容を識別するハッシュを記録する。
import io  # 解読済み文字列を、ファイルのようにcsv.readerへ渡す。
import json  # 原本情報をJSONで保存する。
import math  # NaNや無限大の検出に使う。
from collections import Counter  # 検査状況の件数を集計する。
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
MAPPING = BASE / "japan_travel_weather_destinations_60_coverage_check.csv"
START, END = date(2016, 1, 1), date(2025, 12, 31)
EXPECTED = {START + timedelta(days=i) for i in range((END - START).days + 1)}
METRICS = {"temp": "最高気温(℃)", "precip": "降水量の合計(mm)"}


def read_mapping(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    # 履歴チェックが済んだものだけを、今回の取得対象にする。
    eligible = [r for r in rows if r["coverage_status"].startswith("HISTORY_OK")]
    names = [r["気象庁の観測所"] for r in eligible]
    if not names or any(not name for name in names) or len(names) != len(set(names)):
        raise ValueError("取得対象の観測所名が空、または重複しています。対応表を確認してください。")
    # このCSV形式では観測所番号が取得できないため、名前の一意性を必須とする。
    return rows, {r["気象庁の観測所"]: r for r in eligible}


def number(text, integer=False):
    """空欄をNoneに、数値をint/floatに変換。不正な表記は見逃さない。"""
    text = text.strip()
    if not text:
        return None
    value = int(text) if integer else float(text)
    if not math.isfinite(value):
        raise ValueError(f"有限の数値ではありません: {text}")
    return value


def scan_file(path, allowed, observations, outside):
    """1ファイルを読み、観測所→日付→項目の辞書に蓄積する。"""
    raw = path.read_bytes()
    try:
        text, encoding = raw.decode("utf-8-sig"), "utf-8-sig"
    except UnicodeDecodeError:
        text, encoding = raw.decode("cp932"), "cp932"
    rows = list(csv.reader(io.StringIO(text)))

    # ヘッダー行数を固定せず「年月日」を探す。2項目でも6項目でも対応できる。
    header = next((i for i, r in enumerate(rows) if r and r[0] == "年月日"), None)
    if header is None or header == 0:
        raise ValueError(f"{path.name}: 日付1列のCSVではありません。")
    first_data = next((i for i in range(header + 1, len(rows))
                       if rows[i] and rows[i][0].strip()), None)
    if first_data is None:
        raise ValueError(f"{path.name}: 日別データがありません。")
    stations, items, details = rows[header - 1], rows[header], rows[first_data - 1]
    width = len(items)
    if len(stations) != width or len(details) != width:
        raise ValueError(f"{path.name}: 地点・項目・品質情報のヘッダーが一致しません。")
    names = list(dict.fromkeys(stations[1:]))
    unknown = set(names) - set(allowed)
    if unknown:
        raise ValueError(f"{path.name}: 取得対象にない観測所です: {sorted(unknown)}")

    positions = {}
    for i in range(1, width):
        key = stations[i], items[i], details[i]
        if key in positions:
            raise ValueError(f"{path.name}: 重複するヘッダー: {key}")
        positions[key] = i
    required = [(s, label, info) for s in names for label in METRICS.values()
                for info in ("", "品質情報", "均質番号")]
    missing = [key for key in required if key not in positions]
    if missing:
        raise ValueError(f"{path.name}: 必須列がありません: {missing}")

    for line, row in enumerate(rows[first_data:], start=first_data + 1):
        if len(row) != width:
            raise ValueError(f"{path.name}:{line}: 列数が違います。")
        try:
            day = datetime.strptime(row[0], "%Y/%m/%d").date()
        except ValueError as error:
            raise ValueError(f"{path.name}:{line}: 日付が不正です: {row[0]}") from error
        for station in names:
            if day not in EXPECTED:
                outside.setdefault(station, set()).add(day)
                continue  # 期間外の値は有効日数に加えない。結果には警告を残す。
            days = observations.setdefault(station, {})
            if day in days:
                # 同じ内容でも止める。コピーや再取得分による二重計上を防ぐ。
                raise ValueError(f"{path.name}:{line}: 地点＋日付が重複: {station} {day}")
            record = {}
            for metric, label in METRICS.items():
                try:
                    value = number(row[positions[station, label, ""]])
                    quality = number(row[positions[station, label, "品質情報"]], integer=True)
                    homogeneity = number(row[positions[station, label, "均質番号"]], integer=True)
                    if metric == "precip" and value is not None and value < 0:
                        raise ValueError("降水量が負の値です。")
                except ValueError as error:
                    raise ValueError(f"{path.name}:{line}: {station}/{label}: {error}") from error
                record[metric] = (value, quality, homogeneity)
            days[day] = record
    # 期間外しかない地点も「取得済みだが対象期間なし」として検査対象に残す。
    for station in names:
        observations.setdefault(station, {})
    return {"path": str(path.resolve()), "encoding": encoding,
            "sha256": hashlib.sha256(raw).hexdigest(), "stations": names,
            "download_header": rows[0]}


def summarize(days, outside_dates):
    """日付の完全性と、各指標の品質・均質番号を別々に数える。"""
    absent = len(EXPECTED - set(days))
    result = {"coverage_start": min(days).isoformat() if days else "",
              "coverage_end": max(days).isoformat() if days else "",
              "observed_days": len(days), "missing_date_days": absent,
              "outside_period_days": len(outside_dates)}
    warnings = []
    for metric in METRICS:
        values = [record[metric] for record in days.values()]
        valid = sum(v is not None and q == 8 for v, q, h in values)
        # missingは値の空欄＋日付行の欠落。品質不良の数値とは区別する。
        missing = absent + sum(v is None for v, q, h in values)
        rejected = sum(v is not None and q != 8 for v, q, h in values)
        groups = sorted({h for v, q, h in values if h is not None})
        unknown_h = sum(h is None for v, q, h in values)
        result.update({f"{metric}_valid_days": valid,
                       f"missing_{metric}_days": missing,
                       f"{metric}_quality_rejected_days": rejected,
                       f"{metric}_homogeneity_groups": len(groups),
                       f"{metric}_homogeneity_values": ";".join(map(str, groups)),
                       f"{metric}_homogeneity_missing_days": unknown_h})
        assert valid + missing + rejected == len(EXPECTED)
        if len(groups) > 1:
            warnings.append(f"{metric}:均質番号が複数")
        if unknown_h:
            warnings.append(f"{metric}:均質番号に空欄")
    # 日別CSVで番号が1種類でも、観測所履歴が完全に問題なしとは断定しない。
    result["homogeneity_warning"] = ";".join(warnings) if warnings else "取得範囲で変化検出なし"
    if absent == len(EXPECTED):
        result["homogeneity_warning"] = "対象期間の日別データなし"
    if absent or outside_dates or warnings:
        status = "DAILY_REVIEW"
    elif any(result[f"{m}_valid_days"] != len(EXPECTED) for m in METRICS):
        status = "DAILY_COMPLETE_WITH_EXCLUSIONS"
    else:
        status = "DAILY_COMPLETE_VALID"
    result["daily_scan_status"] = status
    return result


def run(mapping, input_dir, output):
    rows, allowed = read_mapping(mapping)
    files = sorted(input_dir.glob("*.csv"))
    # 閲覧用の_utf8.csvが原本と一緒にある場合、文字列が一致すれば原本だけ検査する。
    # UTF-8版だけのフォルダも従来どおり読める。別名ファイルの重複は引き続きエラー。
    for path in files.copy():
        if path.stem.endswith("_utf8"):
            original = path.with_name(path.stem.removesuffix("_utf8") + ".csv")
            if original.exists():
                raw = original.read_bytes()
                try:
                    original_text = raw.decode("utf-8-sig")
                except UnicodeDecodeError:
                    original_text = raw.decode("cp932")
                if path.read_bytes().decode("utf-8-sig") != original_text:
                    raise ValueError(f"{path.name}: 原本とUTF-8版の内容が違います。")
                files.remove(path)
    if not files:
        raise ValueError(f"CSVがありません: {input_dir}（原本をこのフォルダに保存してください）")
    observations, outside, manifest = {}, {}, []
    for path in files:
        manifest.append(scan_file(path, allowed, observations, outside))
        print(f"検査: {path.name}")
    # 元の対応表を保持し、日別の判定は別列にする。REVIEWを勝手に解除しない。
    for row in rows:
        station = row["気象庁の観測所"]
        if not row["coverage_status"].startswith("HISTORY_OK"):
            row["daily_scan_status"] = "NOT_TARGET"
        elif station not in observations:
            row["daily_scan_status"] = "NOT_DOWNLOADED"
        else:
            row.update(summarize(observations[station], outside.get(station, set())))
            row["daily_source_files"] = ";".join(Path(f["path"]).name for f in manifest
                                                if station in f["stations"])
    columns = list(dict.fromkeys(key for row in rows for key in row))
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.resolve() == mapping.resolve():
        raise ValueError("原本の対応表は上書きできません。別の出力先を指定してください。")
    with output.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    metadata = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
                "source": "https://www.data.jma.go.jp/risk/obsdl/",
                "period": [str(START), str(END)], "valid_quality": 8,
                "station_identity": "CSVの地点名と対応表を照合。観測所番号・位置の再検証はしない。",
                "files": manifest}
    output.with_suffix(".manifest.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(dict(Counter(row["daily_scan_status"] for row in rows)))
    print(f"保存しました: {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", type=Path, default=MAPPING)
    parser.add_argument("--input-dir", type=Path, default=BASE / "data/raw/jma_daily_57")
    parser.add_argument("--output", type=Path, default=BASE / "data/processed/coverage_daily_check.csv")
    parser.add_argument("--list-stations", action="store_true", help="取得対象の観測所を表示する")
    args = parser.parse_args()
    try:
        if args.list_stations:
            _, stations = read_mapping(args.mapping)
            for i, row in enumerate(stations.values(), start=1):
                print(f"{i:02d}. {row['都道府県']} / {row['気象庁の観測所']} "
                      f"({row['観測所番号']}) ← {row['旅行先名']}")
            print(f"取得対象: {len(stations)}観測所")
        else:
            run(args.mapping, args.input_dir, args.output)
    except (ValueError, OSError) as error:
        parser.exit(1, f"検査を中止しました: {error}\n")


if __name__ == "__main__":
    main()
