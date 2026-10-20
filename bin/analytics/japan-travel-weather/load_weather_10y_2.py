import duckdb

# 1地点分の20列を定義する。並び順はCSVと合わせる。
metrics = {
    "temp_mean_c": "DOUBLE",
    "temp_mean_quality": "INTEGER",
    "temp_mean_homogeneity": "INTEGER",
    "temp_max_c": "DOUBLE",
    "temp_max_quality": "INTEGER",
    "temp_max_homogeneity": "INTEGER",
    "temp_min_c": "DOUBLE",
    "temp_min_quality": "INTEGER",
    "temp_min_homogeneity": "INTEGER",
    "precipitation_mm": "DOUBLE",
    "precipitation_no_event": "INTEGER",
    "precipitation_quality": "INTEGER",
    "precipitation_homogeneity": "INTEGER",
    "sunshine_hours": "DOUBLE",
    "sunshine_no_event": "INTEGER",
    "sunshine_quality": "INTEGER",
    "sunshine_homogeneity": "INTEGER",
    "relative_humidity_mean_pct": "DOUBLE",
    "relative_humidity_mean_quality": "INTEGER",
    "relative_humidity_mean_homogeneity": "INTEGER",
}

# CSVの左から順に、地点IDと表示名を定義する。
stations = [("sapporo", "Sapporo"), ("naha", "Naha")]

# 日付は両地点に共通なので、最初に1列だけ用意する。
columns = {"date": "DATE"}

# 各地点の20列を追加して、合計41列の定義を作る。
for station_id, station_name in stations:
    for name, data_type in metrics.items():
        # 例：sapporo_temp_max_c。地点ごとに異なる列名にする。
        columns[f"{station_id}_{name}"] = data_type

# 2地点が横に並んだまま、まずCSVを読み込む。
duckdb.read_csv(
    "data/interim/jma_sapporo_naha_daily_2016_2025_utf8.csv",
    header=False,
    skiprows=6,  # PythonのAPIでは、SQLのskipとは名前が異なる。
    date_format="%Y/%m/%d",
    columns=columns,
).create_view("weather_wide")  # SQLから参照できる名前を付ける。

# 地点ごとのSELECT文を入れるリスト。
queries = []

for station_id, station_name in stations:
    # 地点付きの列名を、これまでの共通の列名に戻す。
    # 例：sapporo_temp_max_c AS temp_max_c
    fields = ", ".join(
        f"{station_id}_{name} AS {name}"
        for name in metrics
    )

    # 1地点分のデータを取り出すSQLを作る。
    query = f"""
        SELECT
            '{station_id}' AS destination_id,
            '{station_name}' AS station_name,
            date,
            {fields}
        FROM weather_wide
    """
    queries.append(query)  # 作ったSQLをリストに追加する。

# UNION ALLは、同じ列構成の結果を縦につなぐ。
duckdb.sql(
    "CREATE OR REPLACE TEMP VIEW weather_daily AS "
    + " UNION ALL ".join(queries)
)

duckdb.sql("DESCRIBE weather_daily").show()

duckdb.sql(
  """
  SELECT *
  FROM weather_daily
  LIMIT 5;
  """
).show()

duckdb.sql(
  """
  SELECT
      count(*) AS row_count,
      min(date) AS first_date,
      max(date) AS last_date
  FROM weather_daily;
  """
).show()

duckdb.sql(
    """
    SELECT
        temp_mean_quality,
        count(*) AS days
    FROM weather_daily
    GROUP BY temp_mean_quality
    ORDER BY temp_mean_quality
    """
).show()

duckdb.sql(
    """
    SELECT
        count(*) AS rows,
        count(DISTINCT date) AS unique_dates,
        count(*) - count(temp_mean_c) AS missing_temp_mean
    FROM weather_daily;
    """
).show()

duckdb.sql(
    """
    SELECT
        'temp_max' AS metric,
        temp_max_quality AS quality,
        count(*) AS days,
        count(*) - count(temp_max_c) AS missing
    FROM weather_daily
    GROUP BY temp_max_quality

    UNION ALL

    SELECT
        'temp_min',
        temp_min_quality,
        count(*),
        count(*) - count(temp_min_c)
    FROM weather_daily
    GROUP BY temp_min_quality

    UNION ALL

    SELECT
        'precipitation',
        precipitation_quality,
        count(*),
        count(*) - count(precipitation_mm)
    FROM weather_daily
    GROUP BY precipitation_quality

    UNION ALL

    SELECT
        'sunshine',
        sunshine_quality,
        count(*),
        count(*) - count(sunshine_hours)
    FROM weather_daily
    GROUP BY sunshine_quality

    UNION ALL

    SELECT
        'relative_humidity',
        relative_humidity_mean_quality,
        count(*),
        count(*) - count(relative_humidity_mean_pct)
    FROM weather_daily
    GROUP BY relative_humidity_mean_quality

    ORDER BY metric, quality;
    """
).show()

duckdb.sql(
    """
    SELECT
        date,
        temp_mean_c,
        temp_max_c,
        temp_max_quality,
        temp_min_c
    FROM weather_daily
    WHERE temp_max_quality IS DISTINCT FROM 8
    ORDER BY date;
    """
).show()

duckdb.sql(
    """
    COPY (
        SELECT *
        FROM weather_daily
        ORDER BY destination_id, date
    )
    TO 'data/processed/jma_sapporo_naha_daily_2016_2025.parquet'
    (FORMAT PARQUET);
    """
)

duckdb.sql(
    """
    SELECT
        destination_id,
        count(*) AS days,
        min(date) AS first_date,
        max(date) AS last_date
    FROM read_parquet(
        'data/processed/jma_sapporo_naha_daily_2016_2025.parquet'
    )
    GROUP BY destination_id;
    """
).show()

duckdb.sql(
    """
    SELECT
        count(DISTINCT temp_mean_homogeneity) AS temp_mean_groups,
        count(DISTINCT temp_max_homogeneity) AS temp_max_groups,
        count(DISTINCT temp_min_homogeneity) AS temp_min_groups,
        count(DISTINCT precipitation_homogeneity) AS precipitation_groups,
        count(DISTINCT sunshine_homogeneity) AS sunshine_groups,
        count(DISTINCT relative_humidity_mean_homogeneity) AS relative_humidity_groups
    FROM weather_daily;
    """
).show()
