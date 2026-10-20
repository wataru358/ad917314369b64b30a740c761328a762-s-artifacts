from pathlib import Path

import duckdb


DATA_DIR = Path(__file__).resolve().parent / "data" / "processed"
con = duckdb.connect()

try:
    con.read_csv(
        str(DATA_DIR / "weather_accommodation_56_regions.csv"),
        header=True,
        dtype={"prefecture_code": "VARCHAR"},
    ).create_view("combined")

    # 56地点×12か月が重複なくそろっているか確認する。
    keys = con.sql(
        "SELECT destination_id, start_month FROM combined"
    ).fetchall()
    ids = {d for d, _ in keys}
    expected = {(d, m) for d in ids for m in range(1, 13)}

    if (
        None in ids
        or len(ids) != 56
        or len(keys) != 672
        or set(keys) != expected
    ):
        raise ValueError("入力の旅行先・月に不足、余分、重複があります。")

    invalid = con.sql("""
        SELECT count(*) FROM combined
        WHERE demand_ratio_mean IS NULL
           OR NOT isfinite(demand_ratio_mean)
           OR demand_ratio_mean < 0
           OR (matching_trips_pct IS NOT NULL AND (
               NOT isfinite(matching_trips_pct)
               OR matching_trips_pct NOT BETWEEN 0 AND 100
           ))
    """).fetchone()[0]
    if invalid:
        raise ValueError("比率または気象達成率を確認してください。")

    # 各行を4つの係数で評価する。今回は比較のため下限を設けない。
    # 閑散期は加点せず、年間平均を上回った分だけ減点する。
    con.sql("""
        CREATE TEMP TABLE ranked AS
        WITH scored AS (
            SELECT c.*, k.coefficient,
                k.coefficient * greatest(demand_ratio_mean - 1, 0)
                    AS demand_penalty,
                matching_trips_pct - demand_penalty AS total_score
            FROM combined AS c
            CROSS JOIN (VALUES (0), (10), (20), (30)) AS k(coefficient)
        )
        SELECT *,
            -- 同じ月・同じ係数の56地点で比較する。同点は同順位。
            -- 気象達成率がNULLなら、スコアも順位もNULLのまま残す。
            CASE WHEN total_score IS NOT NULL THEN
                rank() OVER (
                    PARTITION BY start_month, coefficient
                    ORDER BY total_score DESC NULLS LAST
                )
            END AS month_rank
        FROM scored
    """)

    # 係数0の順位と比べる。正の値なら順位が上がったことを表す。
    con.sql("""
        CREATE TEMP TABLE comparison AS
        SELECT r.*, b.month_rank AS weather_rank,
            b.month_rank - r.month_rank AS rank_change
        FROM ranked AS r
        JOIN ranked AS b
            ON r.destination_id = b.destination_id
           AND r.start_month = b.start_month
           AND b.coefficient = 0
    """)

    if con.sql(
        "SELECT count(*) FROM comparison"
    ).fetchone()[0] != 2688:
        raise ValueError("比較結果が672行×4係数になっていません。")

    if con.sql("""
        SELECT count(*) FROM comparison
        WHERE coefficient = 0
          AND total_score IS DISTINCT FROM matching_trips_pct
    """).fetchone()[0]:
        raise ValueError("係数0のスコアが元の気象達成率と一致しません。")

    # 月・係数ごとに、順位の変化と上位10位への出入りを集計する。
    con.sql("""
        CREATE TEMP TABLE sensitivity AS
        SELECT start_month, coefficient,
            count(month_rank) AS ranked_places,
            count(*) FILTER (
                WHERE rank_change <> 0
            ) AS changed_places,
            max(abs(rank_change)) AS max_rank_change,
            count(*) FILTER (
                WHERE weather_rank <= 10 AND month_rank > 10
            ) AS top10_exits,
            count(*) FILTER (
                WHERE weather_rank > 10 AND month_rank <= 10
            ) AS top10_entries
        FROM comparison
        WHERE coefficient > 0
        GROUP BY start_month, coefficient
    """)

    # 全地点の比較と、係数別・月別の上位を保存する。
    # 同点を含むため、上位10位には11地点以上入る場合がある。
    for query, filename in [
        (
            """
            SELECT * FROM comparison
            ORDER BY start_month, coefficient,
                     month_rank NULLS LAST, destination_id
            """,
            "score_weight_comparison.csv",
        ),
        (
            """
            SELECT * FROM sensitivity
            ORDER BY start_month, coefficient
            """,
            "score_weight_sensitivity.csv",
        ),
        (
            """
            SELECT * FROM comparison
            WHERE month_rank <= 10
            ORDER BY start_month, coefficient, month_rank, destination_id
            """,
            "score_weight_top10.csv",
        ),
    ]:
        con.sql(query).write_csv(
            str(DATA_DIR / filename), header=True
        )
        print(f"保存: {filename}")

    # 端末幅で列が省略されないよう、必要な項目を1行ずつ表示する。
    print("\n月  係数  順位変動地点数  最大変動  上位10位から退出/へ進入")
    for m, k, _, changed, maximum, exits, entries in con.sql("""
        SELECT * FROM sensitivity
        ORDER BY start_month, coefficient
    """).fetchall():
        print(
            f"{m:2}  {k:4}  {changed:14}  "
            f"{str(maximum):>8}  {exits:4}/{entries}"
        )

    print("\n検査OK: 2,688行、係数0のスコアは元の気象達成率と一致")

finally:
    con.close()
