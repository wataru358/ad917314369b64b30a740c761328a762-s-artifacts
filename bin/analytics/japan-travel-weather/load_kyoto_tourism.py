"""京都市の2本のPDFを照合し、暦年2023〜2025年の月別CSVを作る。

対象は総数・日帰り・宿泊実人数・宿泊延べ人数。国籍別は含めない。
PDFの表配置に合わせた読み取りなので、別年版へ使い回す際は原表を確認する。
"""
import csv
import hashlib
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader


BASE = Path(__file__).resolve().parent
INPUT = BASE / "data" / "tourism" / "kyoto"
OUTPUT = BASE / "data" / "processed"
# ページ番号は、表紙を1枚目としたPDF内の位置。
SOURCES = [
    (2024, "R6honsatsu.pdf", 15, 16,
     "https://www.city.kyoto.lg.jp/sankan/cmsfiles/contents/0000109/109809/R6honsatsu.pdf"),
    (2025, "honsatsu.pdf", 19, 20,
     "https://www.city.kyoto.lg.jp/sankan/cmsfiles/contents/0000354/354593/honsatsu.pdf"),
]
METRICS = (
    "visitors_thousands", "day_visitors_thousands",
    "overnight_visitors_thousands", "guest_nights_thousands",
)
# 数値だけを拾うとグラフの目盛りも混ざる。月別行全体の形を指定する。
NUMBER = r"(\d+(?:,\d{3})*(?:\.\d+)?)"
HALF = rf"(\d{{1,2}})\s*月\s+{NUMBER}\s+{NUMBER}\s+{NUMBER}"
MONTH_ROW = re.compile(rf"^\s*{HALF}\s+{HALF}\s*$")
TOTAL_HALF = rf"合\s*計\s+{NUMBER}\s+{NUMBER}\s+{NUMBER}"
TOTAL_ROW = re.compile(rf"^\s*{TOTAL_HALF}\s+{TOTAL_HALF}\s*$")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_table(reader, page_number, report_year, kind):
    """左右2年分の月別12行と合計行を読む。列ずれ・不足は停止する。"""
    text = reader.pages[page_number - 1].extract_text(extraction_mode="layout")
    text = unicodedata.normalize("NFKC", text)
    compact = re.sub(r"\s+", "", text)
    title = "1観光客数" if kind == "visitors" else "2宿泊客数"
    labels = ("総数", "日帰り", "宿泊") if kind == "visitors" else (
        "延べ人数", "実人数", "平均宿泊日数")
    where = f"{report_year}年版/PDF {page_number}枚目"
    require(compact.startswith(title), f"{where}: 表題が違います")
    require(all(label in compact for label in labels) and "(千人)" in compact,
            f"{where}: 列名・単位を確認してください")
    years = [int(y) + 2018 for y in re.findall(r"令和(\d+)年", compact)[:2]]
    require(years == [report_year, report_year - 1], f"{where}: 左右の年が違います")
    monthly, annual = {}, {}
    found_total = False
    for line in text.splitlines():
        match = MONTH_ROW.fullmatch(line)
        if match:
            parts = match.groups()
            require(parts[0] == parts[4], f"{where}: 左右の月が違います")
            for side, year in enumerate(years):
                offset = side * 4
                month = int(parts[offset])
                key = (year, month)
                require(key not in monthly, f"{where}: 月が重複しています")
                values = [v.replace(",", "") for v in parts[offset + 1:offset + 4]]
                # 人数・人泊は千単位の整数。平均宿泊日数だけ小数。
                monthly[key] = tuple(int(v) for v in values) if kind == "visitors" else (
                    int(values[0]), int(values[1]), float(values[2]))
            continue
        match = TOTAL_ROW.fullmatch(line)
        if match:
            values = [v.replace(",", "") for v in match.groups()]
            for side, year in enumerate(years):
                v = values[side * 3:side * 3 + 3]
                annual[year] = tuple(int(x) for x in v) if kind == "visitors" else (
                    int(v[0]), int(v[1]), float(v[2]))
            found_total = True
            break  # 下のグラフや国籍別の参考表は読まない。
    expected = {(y, m) for y in years for m in range(1, 13)}
    require(found_total and set(monthly) == expected and set(annual) == set(years),
            f"{where}: 月別12行または合計行が読めません")
    return monthly, annual


def rounding_check(checks, filename, year, month, metric, reported, calculated, n):
    # 各値を千単位で四捨五入すると誤差は最大0.5。
    # n個の丸めた値の合計と、別途丸めた総数の差は最大(n+1)*0.5。
    # 範囲内でも丸めが原因と断定しない。差をCSVに残す。
    difference = calculated - reported
    bound = (n + 1) * 0.5
    require(abs(difference) <= bound,
            f"合計差が丸め幅を超えました: {filename}/{year}/{month}/{metric}: {difference}")
    checks.append(dict(
        source_file=filename, year=year, month=month, check=metric,
        reported_thousands=reported, calculated_thousands=calculated,
        difference_thousands=difference, rounding_bound_thousands=bound,
        status="exact" if difference == 0 else "within_rounding_bound",
    ))


def save_csv(name, rows):
    path = OUTPUT / name
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"保存: {name} / {len(rows)}行")


def main():
    all_rows, checks, annual_by_report = [], [], {}
    for report_year, filename, visitor_page, lodging_page, url in SOURCES:
        path = INPUT / filename
        source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        reader = PdfReader(path)
        cover = re.sub(r"\s+", "", unicodedata.normalize("NFKC", reader.pages[0].extract_text()))
        require(f"({report_year})年" in cover and "京都観光総合調査" in cover,
                f"{filename}: 表紙の年または資料名が違います")
        visitors, visitor_totals = parse_table(reader, visitor_page, report_year, "visitors")
        lodging, lodging_totals = parse_table(reader, lodging_page, report_year, "lodging")
        for (year, month), (total, day, overnight) in sorted(visitors.items()):
            nights, actual, average_stay = lodging[year, month]
            require(actual == overnight, f"{filename}/{year}/{month}: 2表の宿泊実人数が不一致")
            require(nights >= actual and average_stay >= 1,
                    f"{filename}/{year}/{month}: 宿泊延べ人数・平均泊数を確認してください")
            rounding_check(checks, filename, year, month, "total_vs_parts", total, day + overnight, 2)
            all_rows.append(dict(
                year=year, month=month, destination_id="kyoto", municipality="京都市",
                **dict(zip(METRICS, (total, day, overnight, nights))),
                source_report_year=report_year, source_file=filename,
                source_visitors_pdf_page=visitor_page,
                source_guest_nights_pdf_page=lodging_page,
                source_visitors_printed_page=visitor_page - 2,
                source_guest_nights_printed_page=lodging_page - 2,
                source_table_side="left" if year == report_year else "right",
                source_url=url, source_sha256=source_hash,
            ))
        for year, (total, day, overnight) in visitor_totals.items():
            nights, actual, _ = lodging_totals[year]
            require(actual == overnight, f"{filename}/{year}: 2表の年間宿泊実人数が不一致")
            annual = dict(zip(METRICS, (total, day, overnight, nights)))
            annual_by_report[report_year, year] = annual
            rounding_check(checks, filename, year, "", "annual_total_vs_parts", total, day + overnight, 2)
            rows = [r for r in all_rows if r["source_report_year"] == report_year and r["year"] == year]
            for metric in METRICS:
                rounding_check(checks, filename, year, "", metric, annual[metric],
                               sum(r[metric] for r in rows), 12)

    # 同じ2024年の公表値を比べる。ここでは丸め幅を許容しない。
    overlap = []
    indexed = {(r["source_report_year"], r["year"], r["month"]): r for r in all_rows}
    require(len(indexed) == len(all_rows) == 48, "原本別の48か月が一意にそろっていません")
    for month in range(1, 13):
        old, new = indexed[2024, 2024, month], indexed[2025, 2024, month]
        for metric in METRICS:
            overlap.append(dict(
                year=2024, month=month, metric=metric,
                report_2024_value=old[metric], report_2025_value=new[metric],
                difference=new[metric] - old[metric],
                report_2024_file=old["source_file"], report_2025_file=new["source_file"],
            ))
    mismatches = [r for r in overlap if r["difference"] != 0]
    require(not mismatches, f"2024年の資料間不一致。採用前に原表を確認: {mismatches[:5]}")
    require(annual_by_report[2024, 2024] == annual_by_report[2025, 2024],
            "2024年の年計が資料間で一致しません")

    # 2024・2025年は新しい2025年版、2023年は2024年版から採用。
    # 2023年を2026年の遡及修正済み月別値とは表示しない。出典の版を残す。
    selected = sorted(
        (r for r in all_rows if r["source_report_year"] == 2025 or r["year"] == 2023),
        key=lambda r: (r["year"], r["month"]),
    )
    expected = {(y, m) for y in (2023, 2024, 2025) for m in range(1, 13)}
    require(len(selected) == 36 and {(r["year"], r["month"]) for r in selected} == expected,
            "採用する36か月の不足・重複があります")
    # すべての検査を終えてから保存する。原本の値は補正しない。
    OUTPUT.mkdir(parents=True, exist_ok=True)
    save_csv("kyoto_overlap_2024.csv", overlap)
    save_csv("kyoto_tourism_rounding_checks.csv", checks)
    save_csv("kyoto_tourism_monthly_2023_2025.csv", selected)
    print("検査OK: 2024年の月別48値・年計4値が資料間で完全一致")
    print("検査OK: 2023〜2025年の36か月、欠損・重複なし")
    nonzero = [r for r in checks if r["difference_thousands"] != 0]
    print(f"合計検査: {len(checks)}件 / 差0は{len(checks) - len(nonzero)}件 / 丸め幅内の差は{len(nonzero)}件")
    for r in nonzero:
        period = f"{r['month']}月" if r['month'] else "年計"
        print(f"  {r['source_file']} {r['year']}年 {period} {r['check']}: 差{r['difference_thousands']:+d}（千単位）")
    print("年別の月合計（千人、guest_nightsのみ千人泊。原表の年計とは区別）")
    for year in (2023, 2024, 2025):
        print(year, {m: sum(r[m] for r in selected if r['year'] == year) for m in METRICS})


if __name__ == "__main__":
    main()
