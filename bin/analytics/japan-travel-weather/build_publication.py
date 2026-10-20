"""既存672行からブログ記事に添える表・図を生成する。分析用データは変更しない。

天候の達成率で順位を付け、宿泊需要は参考情報として併記する。
小数1桁の既存達成率で同順位（1,1,3）とし、微差に順位の意味を持たせすぎない。
"""

import calendar
import csv
import html
import json
from pathlib import Path

import duckdb

from build_trip_calendar import write_csv

BASE = Path(__file__).resolve().parent
DATA = BASE / "data/processed"
OUT = BASE / "publication"
PREFECTURES = (
    "Hokkaido Aomori Iwate Miyagi Akita Yamagata Fukushima Ibaraki Tochigi Gunma "
    "Saitama Chiba Tokyo Kanagawa Niigata Toyama Ishikawa Fukui Yamanashi Nagano "
    "Gifu Shizuoka Aichi Mie Shiga Kyoto Osaka Hyogo Nara Wakayama Tottori Shimane "
    "Okayama Hiroshima Yamaguchi Tokushima Kagawa Ehime Kochi Fukuoka Saga Nagasaki "
    "Kumamoto Oita Miyazaki Kagoshima Okinawa"
).split()
NAMES = {"aizuwakamatsu": "Aizu-Wakamatsu", "shiretoko-utoro": "Shiretoko (Utoro)",
         "shirakawago": "Shirakawa-go", "kawaguchiko": "Lake Kawaguchi",
         "kinosaki": "Kinosaki Onsen", "kusatsu": "Kusatsu Onsen"}


def read_csv(name):
    with (DATA / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def table(rows, include_month=True):
    columns = (["Month"] if include_month else []) + [
        "Rank", "Destination", "Weather match", "Matching / valid starts",
        "Valid coverage", "Lodging area", "Lodging ratio",
    ]
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for r in rows:
        values = ([calendar.month_name[r["start_month"]]] if include_month else []) + [
            str(r["weather_rank"]), r["destination_en"], f'{r["matching_trips_pct"]:.1f}%',
            f'{r["matching_trips"]} / {r["valid_trips"]}', f'{r["valid_trips_pct"]:.1f}%',
            r["prefecture_en"], f'{r["demand_ratio_mean"]:.3f}',
        ]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def heatmap(rows):
    # 月別首位の全地点と東京・京都。色に加え数値を出す。
    ids = sorted({r["destination_id"] for r in rows if r["weather_rank"] == 1} | {"tokyo", "kyoto"})
    lookup = {(r["destination_id"], r["start_month"]): r for r in rows}
    width, height = 1050, 195 + len(ids) * 38
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">Four-day weather matches by start month</title>',
             '<desc id="desc">Historical percentages, 2016–2025. Monthly leaders plus Tokyo and Kyoto. Values are not forecasts.</desc>',
             f'<rect width="{width}" height="{height}" fill="#fafaf7"/>',
             '<g font-family="Arial, sans-serif" fill="#173434">',
             '<text x="24" y="34" font-size="24" font-weight="bold">Four-day weather matches by start month</text>',
             '<text x="24" y="60" font-size="14">2016–2025 · Monthly leaders plus Tokyo and Kyoto · Share of valid starts (%)</text>']
    for m in range(1, 13):
        parts.append(f'<text x="{245 + (m-1)*65}" y="94" text-anchor="middle" font-size="14">{calendar.month_abbr[m]}</text>')
    for i, dest in enumerate(ids):
        y = 108 + 38 * i
        parts.append(f'<text x="24" y="{y+22}" font-size="15">{html.escape(lookup[dest,1]["destination_en"])}</text>')
        for m in range(1, 13):
            v = lookup[dest, m]["matching_trips_pct"]
            x = 214 + (m-1)*65
            t = v / 100
            color = tuple(round(a + (b-a)*t) for a,b in zip((235,243,239),(17,100,101)))
            fill = "#" + "".join(f"{c:02x}" for c in color)
            linear = [c/255/12.92 if c/255 <= 0.04045 else ((c/255+0.055)/1.055)**2.4 for c in color]
            luminance = sum(c*w for c,w in zip(linear,(0.2126,0.7152,0.0722)))
            ink = "#000" if luminance > 0.179 else "#fff"
            parts.append(f'<rect x="{x}" y="{y}" width="62" height="34" rx="3" fill="{fill}"/>')
            parts.append(f'<text x="{x+31}" y="{y+22}" text-anchor="middle" font-size="14" fill="{ink}">{v:.1f}</text>')
    parts += [f'<text x="24" y="{height-43}" font-size="13">Higher values meet the stated temperature and precipitation limits more often.</text>',
              f'<text x="24" y="{height-21}" font-size="13">Source: JMA daily observations; project calculations. Historical shares, not forecasts or overall destination ratings.</text>', '</g></svg>']
    (OUT / "weather-monthly.svg").write_text("\n".join(parts), encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    source = read_csv("weather_accommodation_56_regions.csv")
    con = duckdb.connect()
    station_rows = con.sql(f"""SELECT DISTINCT destination_id, station_id, station_name
        FROM '{DATA / 'jma_56_regions_daily_2016_2025.parquet'}'""").fetchall()
    con.close()
    if len(station_rows) != 56:
        raise ValueError("観測所対応が56地点で一意になっていません")
    stations = {d: (s, n) for d, s, n in station_rows}
    rows = []
    for raw in source:
        r = dict(raw)
        for key in ["start_month", "candidate_trips", "valid_trips", "excluded_trips", "matching_trips", "years_count"]:
            r[key] = int(r[key])
        for key in ["matching_trips_pct", "valid_trips_pct", "demand_ratio_mean", "demand_ratio_min", "demand_ratio_max"]:
            r[key] = float(r[key])  # NULLの場合は黙って0にせず停止する。
        r["destination_en"] = NAMES.get(r["destination_id"], r["destination_id"].capitalize())
        r["prefecture_en"] = PREFECTURES[int(r["prefecture_code"]) - 1]
        r["station_id"], r["station_name"] = stations[r["destination_id"]]
        rows.append(r)
    if len(rows) != 672 or len({(r["destination_id"],r["start_month"]) for r in rows}) != 672:
        raise ValueError("672行のキーを確認してください")
    for r in rows:
        peers = [p for p in rows if p["start_month"] == r["start_month"]]
        r["weather_rank"] = 1 + sum(p["matching_trips_pct"] > r["matching_trips_pct"] for p in peers)
        r["ranking_basis"] = "weather_only_rounded_to_0.1_pct"
    rows.sort(key=lambda r: (r["start_month"], r["weather_rank"], r["destination_id"]))
    write_csv(OUT / "destination_months.csv", rows)
    top = [r for r in rows if r["weather_rank"] <= 3]
    leaders = [r for r in rows if r["weather_rank"] == 1]
    write_csv(OUT / "monthly_top3.csv", top)
    write_csv(OUT / "monthly_leaders.csv", leaders)
    weights = read_csv("score_weight_comparison.csv")
    risks = []
    for coef in (10,20,30):
        group = [r for r in weights if int(r["coefficient"]) == coef]
        risks.append({"coefficient":coef,
            "changed_destination_months":sum(int(r["rank_change"]) != 0 for r in group),
            "negative_scores":sum(float(r["total_score"]) < 0 for r in group),
            "zero_weather_promoted":sum(float(r["matching_trips_pct"]) == 0 and int(r["rank_change"]) > 0 for r in group),
            "max_rank_change":max(abs(int(r["rank_change"])) for r in group),
            "months_with_changed_leader":len({r["start_month"] for r in group if (int(r["weather_rank"]) == 1) != (int(r["month_rank"]) == 1)}),
        })
    write_csv(OUT / "score_policy_risks.csv", risks)
    examples = [r for r in weights if r["destination_id"] == "kyoto" and r["start_month"] == "8"]
    write_csv(OUT / "score_policy_kyoto_august.csv", examples)
    heatmap(rows)
    methods = """Ranks use the existing weather percentages rounded to one decimal place. Equal percentages share a rank (1, 1, 3); a top-three group can contain more than three destinations. No lodging penalty or minimum weather cutoff has been applied. A rank describes this comparison, not a promise of suitable weather. Lodging ratios compare each prefecture with its own annual average; 1.000 is that average. They do not measure street crowding, hotel prices, or availability."""
    (OUT / "monthly-tables.md").write_text("# Monthly weather comparison\n\n" + methods + "\n\n" + table(top) + "\n", encoding="utf-8")
    (OUT / "build_summary.json").write_text(json.dumps({
        "status": "built", "policy": "weather_only_with_lodging_context",
        "policy_basis": "Rank by weather match rate and show lodging demand as context",
        "rows": len(rows), "top3_rows": len(top), "leader_rows": len(leaders),
        "minimum_valid_coverage_pct": min(r["valid_trips_pct"] for r in rows),
        "score_policy_risks": risks,
    }, indent=2) + "\n")
    print(f"Publication artifacts: {len(rows)} rows, {len(top)} top-three rows, {len(leaders)} leaders; Markdown tables and SVG")


if __name__ == "__main__":
    main()
