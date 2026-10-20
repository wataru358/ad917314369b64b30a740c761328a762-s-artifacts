"""全国展開用の気象分析：複数のParquet → 品質確認 → 4日間集計 → CSV。

実行例（japan-travel-weatherフォルダから）:
    uv run python analyze_weather_all56region.py

分析対象は2016〜2025年。設定した条件で街歩きする旅行を想定する。
結果は過去の日程の該当割合であり、将来の天気の予報ではない。
"""

from datetime import date  # 分析期間を日付として定義し、日数を計算する。
from pathlib import Path  # 実行場所に依存せず、入力・出力ファイルを指定する。

import duckdb  # Parquetの読み込みと、SQLによる集計を担当する。


# ── 1. 入力と出力の設定 ──────────────────────────────────────
# __file__はこのPythonファイルの場所。parentでその親フォルダを取り出す。
# これにより、別のフォルダから実行してもデータの場所がずれない。
BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# load_weather_56.pyで作った、56地点の統合Parquetを読む。
# 品質不良・欠測の行も保持し、分析するときに日程単位で除外する。
INPUT_FILES = [
    PROCESSED_DIR / "jma_56_regions_daily_2016_2025.parquet",
]
START_DATE = date(2016, 1, 1)
END_DATE = date(2025, 12, 31)
EXPECTED_DAYS = (END_DATE - START_DATE).days + 1  # 両端の日を含めて3,653日。


def main():
    # ── 2. 複数ファイルを、共通の表として読み込む ──────────────
    for path in INPUT_FILES:
        if not path.is_file():  # 入力の不足は、分析を始める前に知らせる。
            raise FileNotFoundError(f"入力ファイルが見つかりません: {path}")

    con = duckdb.connect()  # メモリ上のデータベース。元のParquetは変更しない。
    try:
        # リスト内包表記で、PathをDuckDBが受け取れる文字列に変換する。
        # union_by_name=Falseにより、ファイル間の列の不一致を見逃さない。
        con.read_parquet(
            [str(path) for path in INPUT_FILES], union_by_name=False
        ).create_view("weather_daily")  # SQLから参照する表の名前を付ける。

        # ── 3. 地点と日付を検査する ────────────────────────────
        # 同じ日付でも、東京と札幌なら別の観測。重複は「地点＋日付」で判定する。
        # 重複があると、後の「4行＝4日間」という前提が崩れてしまう。
        duplicates = con.sql("""
            SELECT destination_id, date, count(*) AS copies
            FROM weather_daily
            GROUP BY destination_id, date
            HAVING count(*) > 1
        """).fetchall()  # SQLの結果をPythonのリストとして受け取る。
        if duplicates:
            raise ValueError(f"地点と日付が重複しています（先頭5件）: {duplicates[:5]}")

        # 地点名や日付のない行は、どの旅行日程に属するか判断できない。
        invalid_keys = con.sql("""
            SELECT count(*) FROM weather_daily
            WHERE destination_id IS NULL OR trim(destination_id) = '' OR date IS NULL
        """).fetchone()[0]  # 1行目の1列目にある件数を取り出す。
        if invalid_keys:
            raise ValueError(f"地点IDまたは日付がない行が{invalid_keys}件あります。")

        # 地点別の行数・最初の日・最後の日をPython側で確認する。
        spans = con.sql("""
            SELECT destination_id, count(*), min(date), max(date)
            FROM weather_daily GROUP BY destination_id ORDER BY destination_id
        """).fetchall()

        if not spans:
            raise ValueError("入力データが空です。")

        # 入力ファイルを取り違えて、3都市だけで分析を終えないようにする。
        if len(spans) != 56:
            raise ValueError(f"56地点が必要ですが、入力は{len(spans)}地点です。")



        for station, days, first, last in spans:
            # 重複がなく、両端の日付と日数が一致すれば、全日付がそろっている。
            # 気象値の欠測は許すが、日付の行そのものが抜けた入力はここで止める。
            if (days, first, last) != (EXPECTED_DAYS, START_DATE, END_DATE):
                raise ValueError(
                    f"{station}: {first}〜{last}、{days}行です。"
                    f"必要なのは{START_DATE}〜{END_DATE}の{EXPECTED_DAYS}行です。"
                )

        # ── 4. 今回の判定に使う最高気温・降水量の品質を確認する ──
        # 「品質情報=8」かつ「値がNULLでない」日だけを有効とする。
        # 均質番号は観測条件の変化を調べる手掛かり。番号は地点ごとに数える。
        # 複数の番号があれば、記事で比較する前に観測変更の内容を調べる。
        con.sql("""
            CREATE TEMP VIEW weather_quality AS
            SELECT
                destination_id,
                count(*) AS total_days,
                min(date) AS first_date,
                max(date) AS last_date,
                count(*) FILTER (
                    WHERE temp_max_quality = 8 AND temp_max_c IS NOT NULL
                ) AS valid_temp_days,
                count(*) FILTER (
                    WHERE precipitation_quality = 8 AND precipitation_mm IS NOT NULL
                ) AS valid_rain_days,
                count(DISTINCT temp_max_homogeneity) AS temp_max_homogeneity_groups,
                count(DISTINCT precipitation_homogeneity) AS precipitation_homogeneity_groups
            FROM weather_daily
            GROUP BY destination_id
        """)
        print("\n地点別の品質確認（均質番号が複数ある地点は要確認）")
        con.sql("SELECT * FROM weather_quality ORDER BY destination_id").show(max_rows=len(spans))

        # ── 5. 各開始日から4日間の旅行日程を作る ────────────────
        # WINDOWは、集計する行の範囲を指定する仕組み。
        # PARTITION BYで地点を分離し、ORDER BYで日付順に並べる。
        # CURRENT ROW AND 3 FOLLOWINGは「当日＋次の3行」。
        # 先に品質の悪い日を削除すると、離れた日付をつなぐので削除しない。
        con.sql("""
            CREATE TEMP VIEW trips_4d AS
            SELECT
                destination_id,
                date AS start_date,
                count(*) OVER trip AS days_in_window,
                max(date) OVER trip AS end_date,
                -- 以下の有効日数が、それぞれ4日そろう日程だけを評価する。
                count(*) FILTER (
                    WHERE temp_max_quality = 8 AND temp_max_c IS NOT NULL
                ) OVER trip AS valid_temp_days,
                count(*) FILTER (
                    WHERE precipitation_quality = 8 AND precipitation_mm IS NOT NULL
                ) OVER trip AS valid_rain_days,
                -- 猛暑日：最高気温35℃以上。
                count(*) FILTER (
                    WHERE temp_max_quality = 8 AND temp_max_c >= 35
                ) OVER trip AS extreme_heat_days,
                -- 真夏日：最高気温30℃以上。猛暑日もここに含む。
                count(*) FILTER (
                    WHERE temp_max_quality = 8 AND temp_max_c >= 30
                ) OVER trip AS hot_days,
                -- この企画で置く寒さの境界：最高気温10℃未満。
                count(*) FILTER (
                    WHERE temp_max_quality = 8 AND temp_max_c < 10
                ) OVER trip AS cold_days,
                -- 降水日：日降水量1mm以上。雪などによる降水も含みうる。
                count(*) FILTER (
                    WHERE precipitation_quality = 8 AND precipitation_mm >= 1
                ) OVER trip AS rain_days,
                -- この企画で置く強い降水の境界：日降水量30mm以上。
                -- 気象庁の大雨警報などの基準を意味するものではない。
                count(*) FILTER (
                    WHERE precipitation_quality = 8 AND precipitation_mm >= 30
                ) OVER trip AS heavy_rain_days
            FROM weather_daily
            WINDOW trip AS (
                PARTITION BY destination_id
                ORDER BY date
                ROWS BETWEEN CURRENT ROW AND 3 FOLLOWING
            )
        """)

        # ── 6. 日程を評価し、都市×出発月に集計する ──────────────
        # 月またぎ・年またぎも含める。12月31日開始なら12月の旅行と数える。
        # ただし2025年末の最後の3日は、翌年のデータがないので対象外。
        # 2016〜2025年では、各地点に3,650個の完全な4日間ができる。
        con.sql("""
            CREATE TEMP VIEW trip_evaluation AS
            SELECT *,
                -- ANDは両方の条件を満たす場合にtrue（真）になる。
                valid_temp_days = 4 AND valid_rain_days = 4 AS is_valid,
                extreme_heat_days = 0
                    AND hot_days <= 1
                    AND cold_days = 0
                    AND rain_days <= 1
                    AND heavy_rain_days = 0 AS meets_conditions
            FROM trips_4d
            WHERE days_in_window = 4 AND end_date = start_date + 3
        """)
        # is_validとmeets_conditionsを分けるのが重要。
        # 欠測で「雨を数えられなかった日」を「雨がなかった日」と扱わない。
        con.sql("""
            CREATE TEMP VIEW monthly_trip_summary AS
            SELECT
                destination_id,
                month(start_date) AS start_month,
                count(*) AS candidate_trips,
                count(*) FILTER (WHERE is_valid) AS valid_trips,
                candidate_trips - valid_trips AS excluded_trips,
                round(100.0 * valid_trips / candidate_trips, 1) AS valid_trips_pct,
                count(*) FILTER (
                    WHERE is_valid AND meets_conditions
                ) AS matching_trips,
                -- 分母は全日程数ではなく、品質条件を満たした日程数。
                -- NULLIFは有効日程が0件のとき、割合をNULL（計算不可）にする。
                round(
                    100.0 * matching_trips / nullif(valid_trips, 0), 1
                ) AS matching_trips_pct
            FROM trip_evaluation
            GROUP BY destination_id, month(start_date)
        """)
        # 各開始日を同じ重みで数える。年ごとの割合を平均する計算とは異なる。
        # 隣り合う日程は日付が重なるため、互いに独立した実験ではない。
        print("\n都市×出発月の4日間集計（割合の単位は%）")
        con.sql("""
            SELECT * FROM monthly_trip_summary
            ORDER BY destination_id, start_month
        """).show(max_rows=len(spans) * 12)  # 56地点×12か月＝672行を表示する。

        # ── 7. 結果をCSVとして保存する ──────────────────────────
        # 56地点版として保存する。再実行すると、この2ファイルを更新する。
        for view, filename, order in [
            (
                "weather_quality",
                "weather_quality_56_regions.csv",
                "destination_id"
            ),
            (
                "monthly_trip_summary",
                "weather_trip_summary_56_regions.csv",
                "destination_id, start_month"
            ),
        ]:
            target = PROCESSED_DIR / filename
            con.sql(f"SELECT * FROM {view} ORDER BY {order}").write_csv(
                str(target), header=True
            )
            print(f"保存しました: {target}")
    finally:
        con.close()  # 正常終了でも途中でエラーになっても、接続を閉じる。


if __name__ == "__main__":  # このファイルを直接実行したときだけ分析を開始する。
    main()
