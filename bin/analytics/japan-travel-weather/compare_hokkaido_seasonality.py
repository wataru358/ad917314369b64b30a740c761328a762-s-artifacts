from pathlib import Path

import duckdb


DATA_DIR = Path(__file__).resolve().parent / "data" / "processed"
# 市町村全域の統計。特に斜里町はウトロ以外も含む。
MAPPING = [
    ("sapporo", "札幌市"),
    ("otaru", "小樽市"),
    ("hakodate", "函館市"),
    ("furano", "富良野市"),
    ("kushiro", "釧路市"),
    ("shiretoko-utoro", "斜里町"),
]
con = duckdb.connect()


def check_empty(sql, message):
    rows = con.sql(sql).fetchmany(5)
    if rows:
        raise ValueError(f"{message}: {rows}")


def check_keys(table, columns, expected):
    rows = con.sql(f"SELECT {columns} FROM {table}").fetchall()
    if len(rows) != len(expected) or set(rows) != expected:
        raise ValueError(f"{table}: キーの不足・余分・重複があります")


try:
    con.read_parquet(str(
        DATA_DIR / "hokkaido_tourism_monthly_2023_2025.parquet"
    )).create_view("tourism")
    con.read_csv(str(
        DATA_DIR / "weather_accommodation_56_regions.csv"
    ), header=True).create_view("weather")
    con.sql("CREATE TABLE mapping(destination_id VARCHAR, municipality VARCHAR)")
    con.executemany("INSERT INTO mapping VALUES (?, ?)", MAPPING)

    ids = {d for d, _ in MAPPING}
    check_keys("(SELECT * FROM weather WHERE prefecture = '北海道')",
               "destination_id, start_month",
               {(d, m) for d in ids for m in range(1, 13)})

    # 2指標を縦に並べ、同じ計算を適用する。
    # 入込総数は日帰り客を含むため、2指標を足し合わせない。
    con.sql("""
        CREATE TABLE selected AS
        SELECT m.destination_id, t.*, 'visitors' AS metric,
            t.visitors_thousands AS monthly_count_thousands
        FROM tourism t JOIN mapping m USING (municipality)
        UNION ALL
        SELECT m.destination_id, t.*, 'day_visitors' AS metric,
            t.day_visitors_thousands AS monthly_count_thousands
        FROM tourism t JOIN mapping m USING (municipality)
    """)
    metrics = ("visitors", "day_visitors")
    yearly_keys = {(d, y, m, k) for d in ids for y in (2023, 2024, 2025)
                   for m in range(1, 13) for k in metrics}
    check_keys("selected", "destination_id, year, month, metric", yearly_keys)
    check_empty("""
        SELECT * FROM selected WHERE monthly_count_thousands IS NULL
            OR NOT isfinite(monthly_count_thousands)
            OR monthly_count_thousands < 0
    """, "月別人数が不正です")

    # 暦年で計算する。2024年は366日、2月は29日になる。
    con.sql("""
        CREATE TABLE yearly AS
        WITH totals AS (
            SELECT *,
                day(last_day(make_date(year, month, 1))) AS days_in_month,
                make_date(year + 1, 1, 1) - make_date(year, 1, 1)
                    AS days_in_year,
                sum(monthly_count_thousands) OVER (
                    PARTITION BY destination_id, year, metric
                ) AS annual_count_thousands
            FROM selected
        )
        SELECT *,
            (monthly_count_thousands / days_in_month)
                / nullif(annual_count_thousands / days_in_year, 0)
                AS tourism_ratio
        FROM totals
    """)
    check_empty("""
        SELECT * FROM yearly WHERE annual_count_thousands <= 0
            OR tourism_ratio IS NULL OR NOT isfinite(tourism_ratio)
    """, "年間人数または比率が不正です")
    check_empty("""
        SELECT destination_id, year, metric FROM yearly
        GROUP BY destination_id, year, metric
        HAVING abs(sum(tourism_ratio * days_in_month)
                   / max(days_in_year) - 1) > 1e-10
    """, "比率の日数加重平均が1になりません")

    # 各年を同じ重みで平均し、最小・最大で年ごとの幅も残す。
    con.sql("""
        CREATE TABLE monthly AS
        SELECT destination_id, municipality, month, metric,
            count(DISTINCT year) AS tourism_years_count,
            avg(tourism_ratio) AS tourism_ratio_mean,
            min(tourism_ratio) AS tourism_ratio_min,
            max(tourism_ratio) AS tourism_ratio_max
        FROM yearly GROUP BY destination_id, municipality, month, metric
    """)
    con.sql("""
        CREATE TABLE comparison AS
        SELECT m.*, w.destination_name,
            w.matching_trips_pct, w.valid_trips_pct,
            w.years_count AS lodging_years_count,
            w.demand_ratio_mean AS lodging_ratio_mean,
            w.demand_ratio_min AS lodging_ratio_min,
            w.demand_ratio_max AS lodging_ratio_max,
            m.tourism_ratio_mean - w.demand_ratio_mean AS ratio_gap
        FROM monthly m LEFT JOIN weather w
            ON m.destination_id = w.destination_id
            AND m.month = w.start_month
    """)
    check_keys("comparison", "destination_id, month, metric",
               {(d, m, k) for d in ids for m in range(1, 13) for k in metrics})
    check_empty("""
        SELECT * FROM comparison
        WHERE tourism_years_count <> 3 OR lodging_years_count IS DISTINCT FROM 3
            OR lodging_ratio_mean IS NULL OR NOT isfinite(lodging_ratio_mean)
            OR lodging_ratio_min IS NULL OR lodging_ratio_max IS NULL
    """, "結合漏れまたは年数の不一致があります")

    # ピーク月は同率ならすべて残す。差は比率同士の差で、人数差ではない。
    con.sql("""
        CREATE TABLE summary AS
        WITH peaks AS (
            SELECT *,
                max(tourism_ratio_mean) OVER (
                    PARTITION BY destination_id, metric) AS tourism_peak,
                max(lodging_ratio_mean) OVER (
                    PARTITION BY destination_id, metric) AS lodging_peak
            FROM comparison
        )
        SELECT destination_id, destination_name, municipality, metric,
            string_agg(CAST(month AS VARCHAR), ',' ORDER BY month)
                FILTER (WHERE tourism_ratio_mean = tourism_peak)
                AS tourism_peak_months,
            string_agg(CAST(month AS VARCHAR), ',' ORDER BY month)
                FILTER (WHERE lodging_ratio_mean = lodging_peak)
                AS lodging_peak_months,
            avg(abs(ratio_gap)) AS mean_absolute_gap,
            max(abs(ratio_gap)) AS max_absolute_gap,
            count(*) FILTER (
                WHERE (tourism_ratio_mean > 1 AND lodging_ratio_mean < 1)
                   OR (tourism_ratio_mean < 1 AND lodging_ratio_mean > 1)
            ) AS opposite_season_months
        FROM peaks GROUP BY destination_id, destination_name, municipality, metric
    """)
    check_keys("summary", "destination_id, metric",
               {(d, k) for d in ids for k in metrics})

    for table, filename, order in [
        ("yearly", "hokkaido_tourism_ratios_yearly.csv",
         "destination_id, metric, year, month"),
        ("comparison", "hokkaido_seasonality_comparison.csv",
         "destination_id, metric, month"),
        ("summary", "hokkaido_seasonality_summary.csv",
         "destination_id, metric"),
    ]:
        con.sql(f"SELECT * FROM {table} ORDER BY {order}").write_csv(
            str(DATA_DIR / filename), header=True)
        count = con.sql(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"保存: {filename} / {count:,}行")

    print("検査OK: 6地点×36か月×2指標、結合漏れ・重複なし、比率の日数加重平均は1")
    print("visitors=入込総数、day_visitors=日帰り客数")
    con.sql("""
        SELECT destination_name, metric,
            tourism_peak_months, lodging_peak_months,
            round(mean_absolute_gap, 3) AS mean_absolute_gap,
            round(max_absolute_gap, 3) AS max_absolute_gap,
            opposite_season_months
        FROM summary ORDER BY destination_id, metric
    """).show(max_rows=12, max_width=160)
finally:
    con.close()
