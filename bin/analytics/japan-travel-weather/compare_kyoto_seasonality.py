from pathlib import Path

import duckdb


DATA_DIR = Path(__file__).resolve().parent / "data" / "processed"
# 京都市の観光客数と、京都府全体の宿泊需要は地域範囲・調査方法が異なる。
# 既存ランキングは更新せず、比較用CSVだけを作る。
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
    con.read_csv(str(DATA_DIR / "kyoto_tourism_monthly_2023_2025.csv"),
                 header=True).create_view("tourism")
    con.read_csv(str(DATA_DIR / "weather_accommodation_56_regions.csv"),
                 header=True).create_view("weather")
    con.read_csv(str(DATA_DIR / "accommodation_demand_yearly_2023_2025.csv"),
                 header=True).create_view("lodging_yearly")
    ids = {"kyoto"}
    metrics = ("visitors", "day_visitors", "guest_nights")
    check_keys("tourism", "destination_id, year, month",
               {("kyoto", y, m) for y in (2023, 2024, 2025) for m in range(1, 13)})
    check_empty("SELECT * FROM tourism WHERE municipality IS DISTINCT FROM '京都市'",
                "対象市町村が異なります")
    check_keys("(SELECT * FROM weather WHERE destination_id = 'kyoto')",
               "destination_id, start_month", {("kyoto", m) for m in range(1, 13)})
    check_empty("SELECT * FROM weather WHERE destination_id = 'kyoto' AND prefecture IS DISTINCT FROM '京都府'",
                "京都の都道府県が異なります")
    check_keys("(SELECT * FROM lodging_yearly WHERE prefecture = '京都府')", "year, month",
               {(y, m) for y in (2023, 2024, 2025) for m in range(1, 13)})

    # 人数・人泊を直接加算しない。各指標を別々の年間分母で正規化する。
    con.sql("""
        CREATE TABLE selected AS
        SELECT t.*, 'visitors' AS metric, visitors_thousands AS monthly_count_thousands
        FROM tourism t
        UNION ALL
        SELECT t.*, 'day_visitors' AS metric, day_visitors_thousands AS monthly_count_thousands
        FROM tourism t
        UNION ALL
        SELECT t.*, 'guest_nights' AS metric, guest_nights_thousands AS monthly_count_thousands
        FROM tourism t
    """)
    yearly_keys = {("kyoto", y, m, k) for y in (2023, 2024, 2025)
                   for m in range(1, 13) for k in metrics}
    check_keys("selected", "destination_id, year, month, metric", yearly_keys)
    check_empty("""
        SELECT * FROM selected WHERE monthly_count_thousands IS NULL
            OR NOT isfinite(monthly_count_thousands)
            OR monthly_count_thousands < 0
    """, "月別人数が不正です")

    # 暦年で計算する。2024年は366日、2月は29日になる。
    con.sql("""
        CREATE TABLE yearly_base AS
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
    # 地域比率と同じ暦年・月の京都府宿泊比率も残す。
    con.sql("""
        CREATE TABLE yearly AS
        SELECT y.*, l.demand_ratio AS lodging_ratio,
            y.tourism_ratio - l.demand_ratio AS ratio_gap
        FROM yearly_base y LEFT JOIN lodging_yearly l
            ON y.year = l.year AND y.month = l.month AND l.prefecture = '京都府'
    """)
    check_keys("yearly", "destination_id, year, month, metric", yearly_keys)
    check_empty("SELECT * FROM yearly WHERE lodging_ratio IS NULL OR NOT isfinite(lodging_ratio)",
                "年別の宿泊比率の結合に問題があります")
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

    # 年別のピークも保存する。3年平均のピークを「毎年のピーク」と扱わない。
    con.sql("""
        CREATE TABLE yearly_peaks AS
        WITH peaks AS (
            SELECT *, max(tourism_ratio) OVER (PARTITION BY year, metric) AS peak,
                max(lodging_ratio) OVER (PARTITION BY year, metric) AS lodging_peak
            FROM yearly
        )
        SELECT year, metric,
            string_agg(CAST(month AS VARCHAR), ',' ORDER BY month)
                FILTER (WHERE tourism_ratio = peak) AS tourism_peak_months,
            max(peak) AS tourism_peak_ratio,
            string_agg(CAST(month AS VARCHAR), ',' ORDER BY month)
                FILTER (WHERE lodging_ratio = lodging_peak) AS lodging_peak_months
        FROM peaks GROUP BY year, metric
    """)
    check_keys("yearly_peaks", "year, metric", {(y, k) for y in (2023, 2024, 2025) for k in metrics})
    # 記事検討用に、3指標を横に並べる。保存値は丸めない。
    con.sql("""
        CREATE TABLE monthly_overview AS
        SELECT month,
            max(tourism_ratio_mean) FILTER (WHERE metric = 'visitors') AS visitors_ratio,
            max(tourism_ratio_mean) FILTER (WHERE metric = 'day_visitors') AS day_visitors_ratio,
            max(tourism_ratio_mean) FILTER (WHERE metric = 'guest_nights') AS guest_nights_ratio,
            max(lodging_ratio_mean) AS prefecture_lodging_ratio,
            max(matching_trips_pct) AS matching_trips_pct,
            max(valid_trips_pct) AS valid_trips_pct
        FROM comparison GROUP BY month
    """)
    check_keys("monthly_overview", "month", {(m,) for m in range(1, 13)})
    # 2023年を除いた場合も別表で確認。これは2023年の改訂確認の代わりにはならない。
    con.sql("""
        CREATE TABLE recent_comparison AS
        SELECT month, metric, count(*) AS years_count,
            avg(tourism_ratio) AS tourism_ratio_mean,
            avg(lodging_ratio) AS lodging_ratio_mean,
            avg(ratio_gap) AS ratio_gap
        FROM yearly WHERE year IN (2024, 2025) GROUP BY month, metric
    """)
    check_keys("recent_comparison", "month, metric", {(m, k) for m in range(1, 13) for k in metrics})
    check_empty("SELECT * FROM recent_comparison WHERE years_count <> 2", "2年比較の年数が不正です")

    for table, filename, order in [
        ("yearly", "kyoto_tourism_ratios_yearly.csv",
         "destination_id, metric, year, month"),
        ("comparison", "kyoto_seasonality_comparison.csv",
         "destination_id, metric, month"),
        ("summary", "kyoto_seasonality_summary.csv",
         "destination_id, metric"),
        ("yearly_peaks", "kyoto_seasonality_yearly_peaks.csv", "year, metric"),
        ("monthly_overview", "kyoto_seasonality_monthly_overview.csv", "month"),
        ("recent_comparison", "kyoto_seasonality_comparison_2024_2025.csv", "metric, month"),
    ]:
        con.sql(f"SELECT * FROM {table} ORDER BY {order}").write_csv(
            str(DATA_DIR / filename), header=True)
        count = con.sql(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"保存: {filename} / {count:,}行")

    print("検査OK: 1地点×36か月×3指標、結合漏れ・重複なし、比率の日数加重平均は1")
    print("visitors=観光客総数、day_visitors=日帰り客数、guest_nights=宿泊延べ人数")
    con.sql("""
        SELECT destination_name, metric,
            tourism_peak_months, lodging_peak_months,
            round(mean_absolute_gap, 3) AS mean_absolute_gap,
            round(max_absolute_gap, 3) AS max_absolute_gap,
            opposite_season_months
        FROM summary ORDER BY destination_id, metric
    """).show(max_rows=12, max_width=160)
    con.sql("SELECT * FROM yearly_peaks ORDER BY metric, year").show(max_rows=9)
    con.sql("SELECT * FROM monthly_overview ORDER BY month").show(max_rows=12, max_width=150)
finally:
    con.close()
