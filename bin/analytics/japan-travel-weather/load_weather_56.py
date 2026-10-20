"""56地点のUTF-8 CSVを、分析用のParquet 1ファイルにまとめる。

実行：uv run python load_weather_56.py
品質不良・欠測も保存し、この段階ではランキングや日程の評価を行わない。
"""

import csv  # CSVのヘッダーと値を読み、共通の列構成へ並べ替える。
import re  # 観測所番号が5桁であることを確認する。
import tempfile  # 変換途中のファイルを一時フォルダで管理する。
from datetime import datetime
from pathlib import Path

import duckdb  # 型を持つ表への読み込みとParquet保存を担当する。

# 既存の検査コードから、分析期間・対応表・数値変換を再利用する。
from check_weather_coverage import EXPECTED, MAPPING, number, read_mapping

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "data/interim/56_region_to_analyze"
OUTPUT_FILE = BASE_DIR / "data/processed/jma_56_regions_daily_2016_2025.parquet"

# CSVの「項目名＋補助情報名」から、出力列を決める。
# 現象なし情報は気象台には付くが、アメダスでは付かない場合がある。
FIELDS = [
    ("最高気温(℃)", "", "temp_max_c", "DOUBLE"),
    ("最高気温(℃)", "品質情報", "temp_max_quality", "INTEGER"),
    ("最高気温(℃)", "均質番号", "temp_max_homogeneity", "INTEGER"),
    ("降水量の合計(mm)", "", "precipitation_mm", "DOUBLE"),
    ("降水量の合計(mm)", "現象なし情報", "precipitation_no_event", "INTEGER"),
    ("降水量の合計(mm)", "品質情報", "precipitation_quality", "INTEGER"),
    ("降水量の合計(mm)", "均質番号", "precipitation_homogeneity", "INTEGER"),
]

# 観測所番号は計算用の数値ではないので、文字列（VARCHAR）として保存する。
SCHEMA = {
    "destination_id": "VARCHAR",
    "destination_name": "VARCHAR",
    "prefecture": "VARCHAR",
    "station_id": "VARCHAR",
    "station_name": "VARCHAR",
    "date": "DATE",
}
SCHEMA.update({column: dtype for _, _, column, dtype in FIELDS})
SCHEMA["source_file"] = "VARCHAR"  # 各行を元のCSVまでたどれるようにする。


def read_daily(path, station):
    """1地点のCSVを検証し、共通形式の行を順番に返す。"""
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.reader(source))
    # 行数を固定せず「年月日」のヘッダーを探す。
    header = next((i for i, row in enumerate(rows) if row and row[0] == "年月日"), None)
    if header is None or header == 0:
        raise ValueError(f"{path.name}: 日付1列のヘッダーがありません。")
    first_data = next((i for i in range(header + 1, len(rows)) if rows[i] and rows[i][0]), None)
    if first_data is None:
        raise ValueError(f"{path.name}: データがありません。")
    names, items, details = rows[header - 1], rows[header], rows[first_data - 1]
    width = len(items)
    if len(names) != width or len(details) != width:
        raise ValueError(f"{path.name}: ヘッダーの列数が一致しません。")
    if set(names[1:]) != {station["気象庁の観測所"]}:
        raise ValueError(f"{path.name}: ファイルの観測所名と対応表が一致しません。")

    positions = {}  # 例：('最高気温(℃)', '品質情報') → CSV内の列番号。
    for index in range(1, width):
        key = (items[index], details[index])
        if key in positions:
            raise ValueError(f"{path.name}: 重複する列があります: {key}")
        positions[key] = index
    for label, detail, column, _ in FIELDS:
        if (label, detail) not in positions and column != "precipitation_no_event":
            raise ValueError(f"{path.name}: 必須列がありません: {label}/{detail}")

    seen = set()  # 読み込んだ日付を覚え、重複や不足を検出する。
    for line, row in enumerate(rows[first_data:], start=first_data + 1):
        if len(row) != width:
            raise ValueError(f"{path.name}:{line}: 列数が違います。")
        day = datetime.strptime(row[0], "%Y/%m/%d").date()
        if day in seen or day not in EXPECTED:
            raise ValueError(f"{path.name}:{line}: 重複または期間外の日付: {day}")
        seen.add(day)
        values = []
        for label, detail, column, dtype in FIELDS:
            index = positions.get((label, detail))
            # 列自体がない現象なし情報はNone。観測値の空欄もNoneとして保持する。
            try:
                value = None if index is None else number(row[index], integer=dtype == "INTEGER")
                if column == "precipitation_mm" and value is not None and value < 0:
                    raise ValueError("降水量が負の値です。")
            except ValueError as error:
                raise ValueError(f"{path.name}:{line}: {column}: {error}") from error
            values.append(value)
        # yieldは、全地点分をメモリにためずに1行ずつ呼び出し元へ渡す書き方。
        yield [station["destination_id"], station["旅行先名"], station["都道府県"],
               station["観測所番号"], station["気象庁の観測所"], day.isoformat(),
               *values, path.name]
    if seen != EXPECTED:
        raise ValueError(f"{path.name}: 日付が{len(EXPECTED - seen)}日不足しています。")


def main():
    _, candidates = read_mapping(MAPPING)
    # 履歴確認済みの57地点から奈良を保留し、合意した56地点に限定する。
    selected = [row for row in candidates.values() if row["destination_id"] != "nara"]
    if len(selected) != 56 or len({row["destination_id"] for row in selected}) != 56:
        raise ValueError("対応表の対象地点数または旅行先IDを確認してください。")
    inputs = {}
    for station in selected:
        station_id = station["観測所番号"]
        if not re.fullmatch(r"\d{5}", station_id) or station_id in inputs:
            raise ValueError(f"観測所番号が不正、または重複しています: {station_id}")
        inputs[station_id] = INPUT_DIR / f"jma_{station_id}_daily_2016_2025_utf8.csv"
    # ファイルが不足していても、奈良などが混ざっていても、黙って進めない。
    actual = set(INPUT_DIR.glob("*.csv"))
    expected = set(inputs.values())
    if actual != expected:
        raise ValueError(f"入力一覧が違います。不足={expected - actual}、余分={actual - expected}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    # 一時CSVへ共通形式で書き出し、DuckDBで一括読み込みする。
    # 20万行を1行ずつSQLでINSERTするより速く、pandasなどの追加依存も不要。
    with tempfile.TemporaryDirectory(dir=OUTPUT_FILE.parent, prefix=".weather56-") as folder:
        staging = Path(folder) / "normalized.csv"
        with staging.open("w", encoding="utf-8", newline="") as target:
            writer = csv.writer(target)
            writer.writerow(SCHEMA)  # 辞書のキーをヘッダーとして出力する。
            for station in selected:
                writer.writerows(read_daily(inputs[station["観測所番号"]], station))
                print(f"読み込み: {station['旅行先名']} / {station['気象庁の観測所']}", flush=True)

        con = duckdb.connect()
        try:
            # 空欄はNULL、日付はDATE、品質情報はINTEGERとして読み込む。
            con.read_csv(str(staging), header=True, columns=SCHEMA,
                         date_format="%Y-%m-%d").create_view("weather_daily")
            total = con.sql("SELECT count(*) FROM weather_daily").fetchone()[0]
            if total != 56 * len(EXPECTED):
                raise ValueError(f"出力行数が想定と違います: {total}")
            duplicates = con.sql("""
                SELECT destination_id, date FROM weather_daily
                GROUP BY destination_id, date HAVING count(*) > 1
            """).fetchall()
            if duplicates:
                raise ValueError(f"地点＋日付が重複しています: {duplicates[:5]}")

            temporary_output = Path(folder) / "complete.parquet"
            con.sql("SELECT * FROM weather_daily ORDER BY destination_id, date").write_parquet(
                str(temporary_output), compression="zstd"
            )
            # 保存したParquetを読み直し、全列・全行の一致を確認してから正式名へ置く。
            con.read_parquet(str(temporary_output)).create_view("saved")
            difference = con.sql("""
                (SELECT * FROM weather_daily EXCEPT ALL SELECT * FROM saved)
                UNION ALL
                (SELECT * FROM saved EXCEPT ALL SELECT * FROM weather_daily)
                LIMIT 1
            """).fetchall()
            if difference:
                raise ValueError("Parquet保存前後の内容が一致しません。")
            temporary_output.replace(OUTPUT_FILE)  # 成功した場合だけ出力を更新する。
        finally:
            con.close()
    print(f"保存しました: {OUTPUT_FILE}\n56地点 / {total:,}行（分析は未実行）")


if __name__ == "__main__":
    main()
