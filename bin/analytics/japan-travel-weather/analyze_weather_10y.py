import duckdb

duckdb.sql(
    """
    CREATE OR REPLACE TEMP VIEW weather_daily AS
    SELECT *
    FROM read_parquet(
        'data/processed/jma_tokyo_daily_2016_2025.parquet'
    );
    """
)

duckdb.sql(
  """
  SELECT
      month(date) AS month,
      count(*) AS days,
      round(avg(temp_mean_c), 1) AS mean_temp_c
  FROM weather_daily
  WHERE temp_mean_quality = 8
  GROUP BY month(date)
  ORDER BY month;
  """
).show()

# 月別：真夏日・猛暑日の割合
duckdb.sql(
    """
    SELECT
        month(date) AS month,
        count(*) AS valid_temp_days,

        count(*) FILTER (
            WHERE temp_max_c >= 30
        ) AS days_ge_30c,

        round(
            100.0 * count(*) FILTER (
                WHERE temp_max_c >= 30
            ) / count(*),
            1
        ) AS pct_ge_30c,

        count(*) FILTER (
            WHERE temp_max_c >= 35
        ) AS days_ge_35c,

        round(
            100.0 * count(*) FILTER (
                WHERE temp_max_c >= 35
            ) / count(*),
            1
        ) AS pct_ge_35c

    FROM weather_daily
    WHERE
        temp_max_quality = 8
        AND temp_max_c IS NOT NULL
    GROUP BY month(date)
    ORDER BY month;
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
    FROM weather_daily
    WHERE
        precipitation_quality = 8
        AND precipitation_mm IS NOT NULL
    GROUP BY month(date)
    ORDER BY month
    """
).show()

duckdb.sql(
  # 年・月ごとの雨の日の割合
    """
    CREATE OR REPLACE TEMP VIEW monthly_rain_by_year AS
    SELECT
        year(date) AS year,
        month(date) AS month,
        count(*) AS valid_days,
        count(*) FILTER (
            WHERE precipitation_mm >= 1.0
        ) AS rain_days,
        round(
            100.0 * count(*) FILTER (
                WHERE precipitation_mm >= 1.0
            ) / count(*),
            1
        ) AS rain_days_pct
    FROM weather_daily
    WHERE
        precipitation_quality = 8
        AND precipitation_mm IS NOT NULL
    GROUP BY year(date), month(date)
    ORDER BY year, month;
    """
)

duckdb.sql(
    """
    SELECT
        month,
        count(*) AS years,
        min(rain_days) AS min_rain_days,
        max(rain_days) AS max_rain_days,
        round(avg(rain_days), 1) AS mean_rain_days
    FROM monthly_rain_by_year
    GROUP BY month
    ORDER BY month;
    """
).show()

duckdb.sql(
    """
    CREATE OR REPLACE TEMP VIEW monthly_temp_by_year AS
    SELECT
        year(date) AS year,
        month(date) AS month,
        count(*) AS valid_days,
        avg(temp_mean_c) AS mean_temp_c
    FROM weather_daily
    WHERE
        temp_mean_quality = 8
        AND temp_mean_c IS NOT NULL
    GROUP BY year(date), month(date);
    """
)
duckdb.sql(
    """
    SELECT
        month,
        count(*) AS years,
        round(min(mean_temp_c), 1) AS coolest_year_mean_c,
        round(max(mean_temp_c), 1) AS warmest_year_mean_c,
        round(avg(mean_temp_c), 1) AS mean_of_yearly_means_c
    FROM monthly_temp_by_year
    GROUP BY month
    ORDER BY month;
    """
).show()

duckdb.sql(
    """
    SELECT
        year,
        round(mean_temp_c, 1) AS july_mean_temp_c
    FROM monthly_temp_by_year
    WHERE month = 7
    ORDER BY mean_temp_c DESC;
    """
).show()

# 各開始日から4日間の気温・降水を集計
duckdb.sql(
    """
    CREATE OR REPLACE TEMP VIEW trips_4d AS
    SELECT
        destination_id,
        date AS start_date,
        count(*) OVER trip AS days_in_window,
        max(date) OVER trip AS end_date,
        count(*) FILTER (
            WHERE temp_max_quality = 8
              AND temp_max_c IS NOT NULL
        ) OVER trip AS valid_temp_days,
        count(*) FILTER (
            WHERE temp_max_quality = 8
              AND temp_max_c >= 35
        ) OVER trip AS extreme_heat_days,
        count(*) FILTER (
            WHERE temp_max_quality = 8
              AND temp_max_c >= 30
        ) OVER trip AS hot_days,
        count(*) FILTER (
            WHERE precipitation_quality = 8
              AND precipitation_mm IS NOT NULL
        ) OVER trip AS valid_rain_days,
        count(*) FILTER (
            WHERE precipitation_quality = 8
              AND precipitation_mm >= 1.0
        ) OVER trip AS rain_days,
        count(*) FILTER (
            WHERE temp_max_quality = 8
              AND temp_max_c < 10
        ) OVER trip AS cold_days,
        count(*) FILTER (
            WHERE precipitation_quality = 8
              AND precipitation_mm >= 30
        ) OVER trip AS heavy_rain_days
    FROM weather_daily
    WINDOW trip AS (
        PARTITION BY destination_id
        ORDER BY date
        ROWS BETWEEN CURRENT ROW AND 3 FOLLOWING
    );
    """
)
# 出発月別：4日間に猛暑日が1日以上あった日程の割合
duckdb.sql(
    """
    SELECT
        destination_id,
        month(start_date) AS start_month,
        count(*) AS valid_trips,
        count(*) FILTER (
            WHERE extreme_heat_days >= 1
        ) AS trips_with_extreme_heat,
        round(
            100.0 * count(*) FILTER (
                WHERE extreme_heat_days >= 1
            ) / count(*),
            1
        ) AS extreme_heat_trip_pct
    FROM trips_4d
    WHERE
        days_in_window = 4
        AND end_date = start_date + 3
        AND valid_temp_days = 4
    GROUP BY destination_id, month(start_date)
    ORDER BY destination_id, start_month;
    """
).show()
# 出発月別：4日間に雨の日があった日程の割合
duckdb.sql(
    """
    SELECT
        destination_id,
        month(start_date) AS start_month,
        count(*) AS valid_trips,
        count(*) FILTER (
            WHERE rain_days >= 1
        ) AS trips_with_rain,
        round(
            100.0 * count(*) FILTER (
                WHERE rain_days >= 1
            ) / count(*),
            1
        ) AS rain_trip_pct,
        round(
            100.0 * count(*) FILTER (
                WHERE rain_days >= 2
            ) / count(*),
            1
        ) AS two_plus_rain_days_pct
    FROM trips_4d
    WHERE
        days_in_window = 4
        AND end_date = start_date + 3
        AND valid_rain_days = 4
    GROUP BY destination_id, month(start_date)
    ORDER BY destination_id, start_month;
    """
).show()


# 出発月別：猛暑日なし・雨の日が1日以内の日程
duckdb.sql(
    """
    SELECT
        destination_id,
        month(start_date) AS start_month,
        count(*) AS valid_trips,
        count(*) FILTER (
            WHERE extreme_heat_days = 0
              AND rain_days <= 1
        ) AS matching_trips,
        round(
            100.0 * count(*) FILTER (
                WHERE extreme_heat_days = 0
                  AND rain_days <= 1
            ) / count(*),
            1
        ) AS matching_trips_pct
    FROM trips_4d
    WHERE
        days_in_window = 4
        AND end_date = start_date + 3
        AND valid_temp_days = 4
        AND valid_rain_days = 4
    GROUP BY destination_id, month(start_date)
    ORDER BY destination_id, start_month;
    """
).show()


# 条件を満たした8月開始の日程を5件確認する
duckdb.sql(
    """
    SELECT
        start_date,
        end_date,
        extreme_heat_days,
        hot_days,
        rain_days
    FROM trips_4d
    WHERE
        destination_id = 'tokyo'
        AND month(start_date) = 8
        AND days_in_window = 4
        AND end_date = start_date + 3
        AND valid_temp_days = 4
        AND valid_rain_days = 4
        AND extreme_heat_days = 0
        AND rain_days <= 1
    ORDER BY start_date
    LIMIT 5;
    """
).show()

# 4日間の集計を元の日別データと照合
duckdb.sql(
    """
    SELECT
        date,
        temp_max_c,
        temp_max_quality,
        precipitation_mm,
        precipitation_quality,
        temp_max_c >= 35 AS is_extreme_heat,
        precipitation_mm >= 1.0 AS is_rain_day
    FROM weather_daily
    WHERE
        destination_id = 'tokyo'
        AND date BETWEEN DATE '2016-08-03'
        AND DATE '2016-08-06'
    ORDER BY date;
    """
).show()

# 暑さの条件を変えると、該当する日程はどれくらい減るか
duckdb.sql(
    """
    SELECT
        month(start_date) AS start_month,
        count(*) AS valid_trips,
        round(
            100.0 * count(*) FILTER (
                WHERE extreme_heat_days = 0
                  AND rain_days <= 1
            ) / count(*),
            1
        ) AS no_extreme_heat_low_rain_pct,
        round(
            100.0 * count(*) FILTER (
                WHERE extreme_heat_days = 0
                  AND hot_days <= 1
                  AND rain_days <= 1
            ) / count(*),
            1
        ) AS limited_heat_low_rain_pct
    FROM trips_4d
    WHERE
        destination_id = 'tokyo'
        AND days_in_window = 4
        AND end_date = start_date + 3
        AND valid_temp_days = 4
        AND valid_rain_days = 4
    GROUP BY month(start_date)
    ORDER BY start_month;
    """
).show()

# 都市×出発月の集計を、表示にも保存にも使える形にする
duckdb.sql(
    """
    CREATE OR REPLACE TEMP VIEW monthly_trip_summary AS
    SELECT
        destination_id,
        month(start_date) AS start_month,
        count(*) AS valid_trips,
        count(*) FILTER (
            WHERE extreme_heat_days = 0
              AND hot_days <= 1
              AND cold_days = 0
              AND rain_days <= 1
              AND heavy_rain_days = 0
        ) AS matching_trips,
        round(
            100.0 * matching_trips / valid_trips,
            1
        ) AS matching_trips_pct
    FROM trips_4d
    WHERE days_in_window = 4
      AND end_date = start_date + 3
      AND valid_temp_days = 4
      AND valid_rain_days = 4
    GROUP BY destination_id, month(start_date);
    """
)

duckdb.sql(
    """
    SELECT *
    FROM monthly_trip_summary
    ORDER BY destination_id, start_month;
    """
).show()

duckdb.sql(
    """
    COPY (
        SELECT *
        FROM monthly_trip_summary
        ORDER BY destination_id, start_month
    )
    TO 'data/processed/weather_trip_summary.csv'
    (HEADER, DELIMITER ',');
    """
)
