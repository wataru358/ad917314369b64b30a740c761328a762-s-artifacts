import duckdb

duckdb.sql(
  """
  CREATE OR REPLACE TEMP VIEW weather_daily AS
  SELECT *
  FROM read_csv(
      'data/interim/jma_tokyo_daily_2025_utf8.csv',
      header = false,
      skip = 6,
      dateFormat = '%Y/%m/%d',
      columns = {
          'date': 'DATE',

          'temp_mean_c': 'DOUBLE',
          'temp_mean_quality': 'INTEGER',
          'temp_mean_homogeneity': 'INTEGER',

          'temp_max_c': 'DOUBLE',
          'temp_max_quality': 'INTEGER',
          'temp_max_homogeneity': 'INTEGER',

          'temp_min_c': 'DOUBLE',
          'temp_min_quality': 'INTEGER',            'temp_min_homogeneity': 'INTEGER',

          'precipitation_mm': 'DOUBLE',
          'precipitation_no_event': 'INTEGER',
          'precipitation_quality': 'INTEGER',
          'precipitation_homogeneity': 'INTEGER',

          'sunshine_hours': 'DOUBLE',
          'sunshine_no_event': 'INTEGER',            'sunshine_quality': 'INTEGER',
          'sunshine_homogeneity': 'INTEGER',

          'vapor_pressure_mean_hpa': 'DOUBLE',
          'vapor_pressure_mean_quality': 'INTEGER',
          'vapor_pressure_mean_homogeneity': 'INTEGER'
      }
  );
  """
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
        'vapor_pressure',
        vapor_pressure_mean_quality,
        count(*),
        count(*) - count(vapor_pressure_mean_hpa)
    FROM weather_daily
    GROUP BY vapor_pressure_mean_quality

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
        SELECT
            'tokyo' AS destination_id,
            'Tokyo' AS station_name,
            *
        FROM weather_daily
        ORDER BY date
    )
    TO 'data/processed/jma_tokyo_daily_2025.parquet'
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
        'data/processed/jma_tokyo_daily_2025.parquet'
    )
    GROUP BY destination_id;
    """
).show()
