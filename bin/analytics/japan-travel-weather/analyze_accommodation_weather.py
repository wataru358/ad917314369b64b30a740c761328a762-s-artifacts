from pathlib import Path

import duckdb


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"
con = duckdb.connect()


def check_keys(table, columns, expected):
    # 集合で不足・余分を、行数で重複を確認する。
    rows = con.sql(f"SELECT {columns} FROM {table}").fetchall()
    if set(rows) != expected or len(rows) != len(expected):
        raise ValueError(f"{table}: キーに不足・余分・重複があります。")


def check_empty(sql, message):
    # 問題のある行が返ってきたら、先頭5件を表示して止める。
    rows = con.sql(sql).fetchmany(5)
    if rows:
        raise ValueError(f"{message}: {rows}")


try:
    # 既存の宿泊データ、気象集計、旅行先の対応を読み込む。
    con.read_parquet(
        str(DATA_DIR / "accommodation_monthly_2023_2025.parquet")
    ).create_view("lodging")

    con.read_csv(
        str(DATA_DIR / "weather_trip_summary_56_regions.csv"),
        header=True,
    ).create_view("weather")

    con.read_parquet(
        str(DATA_DIR / "jma_56_regions_daily_2016_2025.parquet")
    ).create_view("daily")

    check_keys("lodging", "year, month, prefecture_code", {
        (y, m, f"{p:02d}")
        for y in (2023, 2024, 2025)
        for m in range(1, 13)
        for p in range(1, 48)
    })
    check_empty("""
        SELECT * FROM lodging
        WHERE guest_nights IS NULL OR guest_nights < 0
           OR prefecture IS NULL OR trim(prefecture) = ''
    """, "宿泊者数または都道府県名が不正です")

    con.sql("""
        CREATE TEMP TABLE prefectures AS
        SELECT DISTINCT prefecture_code, prefecture FROM lodging
    """)
    for column in ("prefecture_code", "prefecture"):
        check_empty(f"""
            SELECT {column} FROM prefectures
            GROUP BY {column} HAVING count(*) <> 1
        """, "都道府県コードと名前が一対一になっていません")

    # 年間合計を各月の行に付ける。月の日数とうるう年も反映する。
    con.sql("""
        CREATE TEMP TABLE yearly_ratio AS
        WITH totals AS (
            SELECT *,
                day(last_day(make_date(year, month, 1))) AS days_in_month,
                make_date(year + 1, 1, 1) - make_date(year, 1, 1)
                    AS days_in_year,
                sum(guest_nights) OVER (
                    PARTITION BY year, prefecture_code
                ) AS annual_guest_nights
            FROM lodging
        )
        SELECT *,
            guest_nights * 1.0 / days_in_month
                AS monthly_daily_guest_nights,
            annual_guest_nights * 1.0 / days_in_year
                AS annual_daily_guest_nights,
            (guest_nights * 1.0 / days_in_month)
                / nullif(annual_guest_nights * 1.0 / days_in_year, 0)
                AS demand_ratio
        FROM totals
    """)
    check_empty("""
        SELECT year, prefecture_code FROM yearly_ratio
        WHERE demand_ratio IS NULL OR NOT isfinite(demand_ratio)
           OR annual_guest_nights <= 0
    """, "年間の分母または比率を確認してください")

    check_empty("""
        SELECT year, prefecture_code
        FROM yearly_ratio GROUP BY year, prefecture_code
        HAVING abs(
            sum(demand_ratio * days_in_month) / max(days_in_year) - 1
        ) > 1e-10
    """, "日数で加重平均した比率が1になりません")

    # 3年を同じ重みで平均する。
    # 年ごとの差を見るため、最小・最大も残す。
    con.sql("""
        CREATE TEMP TABLE monthly_ratio AS
        SELECT prefecture_code, prefecture, month,
            count(DISTINCT year) AS years_count,
            avg(demand_ratio) AS demand_ratio_mean,
            min(demand_ratio) AS demand_ratio_min,
            max(demand_ratio) AS demand_ratio_max
        FROM yearly_ratio
        GROUP BY prefecture_code, prefecture, month
    """)
    check_keys("monthly_ratio", "prefecture_code, month", {
        (f"{p:02d}", m)
        for p in range(1, 48)
        for m in range(1, 13)
    })
    check_empty(
        "SELECT * FROM monthly_ratio WHERE years_count <> 3",
        "3年分そろっていない県・月があります",
    )

    # 日別20万行を、旅行先ごとに1行の対応表にする。
    con.sql("""
        CREATE TEMP TABLE destinations AS
        SELECT DISTINCT destination_id, destination_name, prefecture
        FROM daily
    """)
    check_empty("""
        SELECT * FROM destinations
        WHERE destination_id IS NULL OR trim(destination_id) = ''
           OR destination_name IS NULL OR trim(destination_name) = ''
           OR prefecture IS NULL OR trim(prefecture) = ''
    """, "旅行先の対応情報が欠けています")

    check_empty("""
        SELECT destination_id FROM destinations
        GROUP BY destination_id HAVING count(*) <> 1
    """, "旅行先の対応が一意ではありません")

    ids = {
        r[0]
        for r in con.sql(
            "SELECT destination_id FROM destinations"
        ).fetchall()
    }
    if len(ids) != 56:
        raise ValueError(f"旅行先が56地点ではありません: {len(ids)}")

    expected_weather = {(d, m) for d in ids for m in range(1, 13)}
    check_keys("weather", "destination_id, start_month", expected_weather)

    # LEFT JOINで気象の全行を残し、結合漏れは後でエラーにする。
    con.sql("""
        CREATE TEMP TABLE combined AS
        SELECT w.*, d.destination_name, d.prefecture,
            r.prefecture_code, r.years_count,
            r.demand_ratio_mean, r.demand_ratio_min, r.demand_ratio_max
        FROM weather AS w
        LEFT JOIN destinations AS d USING (destination_id)
        LEFT JOIN monthly_ratio AS r
            ON d.prefecture = r.prefecture AND w.start_month = r.month
    """)
    check_keys("combined", "destination_id, start_month", expected_weather)
    check_empty(
        "SELECT * FROM combined WHERE demand_ratio_mean IS NULL",
        "宿泊需要を結合できない地点・月があります",
    )

    # 気象の全列を元データと比較する。NULLもそのまま保持する。
    weather_columns = ", ".join(con.table("weather").columns)
    check_empty(f"""
        (
            SELECT {weather_columns} FROM combined
            EXCEPT ALL SELECT * FROM weather
        )
        UNION ALL
        (
            SELECT * FROM weather
            EXCEPT ALL SELECT {weather_columns} FROM combined
        )
    """, "結合によって気象データが変わっています")

    # 検査を通過してから保存する。
    # 再実行時はこの3ファイルを更新する。
    for table, filename, order in [
        (
            "yearly_ratio",
            "accommodation_demand_yearly_2023_2025.csv",
            "prefecture_code, year, month",
        ),
        (
            "monthly_ratio",
            "accommodation_demand_monthly_2023_2025.csv",
            "prefecture_code, month",
        ),
        (
            "combined",
            "weather_accommodation_56_regions.csv",
            "destination_id, start_month",
        ),
    ]:
        target = DATA_DIR / filename
        con.sql(
            f"SELECT * FROM {table} ORDER BY {order}"
        ).write_csv(str(target), header=True)

        count = con.sql(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"保存: {filename} / {count:,}行")

    print("検査OK: 56地点×12か月、結合漏れ・重複なし、気象の全列一致")

    print("\n宿泊需要比率の分布（47都道府県×12か月）")
    con.sql("""
        SELECT round(min(demand_ratio_mean), 3) AS minimum,
            round(median(demand_ratio_mean), 3) AS median,
            round(max(demand_ratio_mean), 3) AS maximum
        FROM monthly_ratio
    """).show()

    print("\n東京・札幌・那覇の例（表示だけ小数3桁に丸める）")
    con.sql("""
        SELECT destination_id, start_month,
            matching_trips_pct, valid_trips_pct,
            round(demand_ratio_mean, 3) AS demand_ratio_mean,
            round(demand_ratio_min, 3) AS demand_ratio_min,
            round(demand_ratio_max, 3) AS demand_ratio_max
        FROM combined
        WHERE destination_id IN ('tokyo', 'sapporo', 'naha')
        ORDER BY destination_id, start_month
    """).show(max_rows=36)

finally:
    con.close()
