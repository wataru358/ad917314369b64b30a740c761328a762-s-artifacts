import duckdb

duckdb.sql(
  """
  SELECT
      month(date) AS month,
      count(*) AS days,
      round(avg(temp_mean_c), 1) AS mean_temp_c
  FROM read_parquet(
      'data/processed/jma_tokyo_daily_2025.parquet'
  )
  WHERE temp_mean_quality = 8
  GROUP BY month(date)
  ORDER BY month;
  """
).show()

duckdb.sql(
    """
    SELECT
        month(date) AS month,
        count(*) AS valid_Days,
        count(*) FILTER (
          WHERE temp_max_c >= 30
        ) AS hot_days,
        round (
          100.0 * count(*) FILTER (
            WHERE temp_max_c >= 30
          ) / count(*),
          1
        ) AS hot_days_pct
    FROM read_parquet(
        'data/processed/jma_tokyo_daily_2025.parquet'
    )
    WHERE
        temp_max_quality = 8
        AND temp_max_c IS NOT NULL
    GROUP BY month(date)
    ORDER BY month
    """
).show()


# rainy days
duckdb.sql(
    """
    SELECT
        month(date) AS month,
        count(*) AS valid_Days,
        count(*) FILTER (
          WHERE precipitation_mm >= 1.0
        ) AS rain_days,
        round (
          100.0 * count(*) FILTER (
            WHERE precipitation_mm >= 1.0
          ) / count(*),
          1
        ) AS rain_days_pct,
        count(*) FILTER (
          WHERE precipitation_mm >= 30
        ) AS heavy_rain_days,
        round(
            100.0 * count(*) FILTER (
                WHERE precipitation_mm >= 30
            ) / count(*),
            1
        ) AS heavy_rain_days_pct
    FROM read_parquet(
        'data/processed/jma_tokyo_daily_2025.parquet'
    )
    WHERE
        precipitation_quality = 8
        AND precipitation_mm IS NOT NULL
    GROUP BY month(date)
    ORDER BY month
    """
).show()
