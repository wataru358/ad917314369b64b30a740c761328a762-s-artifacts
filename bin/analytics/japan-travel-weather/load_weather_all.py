"""気象庁のUTF-8 CSVをまとめて読み込み、共通形式のParquetを作る。

実行方法：uv run python load_weather_all.py
対象：日別値・日付1列・数値形式・品質情報と均質番号付きのCSV。
文字コード変換はconvert_to_utf8.pyで済ませ、INPUT_FILESに登録する。
"""

import csv  # カンマや引用符を正しく扱って、CSVを行・列に分解する。
import math  # NaNや無限大を、正常な観測値として読み込まないために使う。
import tempfile  # 保存途中のParquetを置く、一時ファイルを作る。
from datetime import date, datetime  # 期間の定義と、日付文字列の変換に使う。
from pathlib import Path  # /演算子でフォルダとファイル名をつなぐ。

import duckdb  # 読み込んだデータを表にして、Parquetへ保存する。


# ── 1. 全国分を増やすときに編集する設定 ──────────────────────
BASE_DIR = Path(__file__).resolve().parent  # このスクリプトのあるフォルダ。
INPUT_FILES = [
    BASE_DIR / "data/interim/jma_tokyo_daily_2016_2025_utf8.csv",
    BASE_DIR / "data/interim/jma_sapporo_naha_daily_2016_2025_utf8.csv",
]
OUTPUT_FILE = BASE_DIR / "data/processed/jma_all_daily_2016_2025.parquet"

# 日本語の観測地点名を、分析に使うID・表示名へ対応させる辞書。
# 新しい地点を取得したら追記する。IDは地点間で重複させないこと。
# 今回のCSVには都道府県名がないため、同名の観測所の区別には未対応。
# 全国展開時は、観測所と旅行先の対応を確認してから登録する。
STATIONS = {
    "東京": ("tokyo", "Tokyo"),
    "札幌": ("sapporo", "Sapporo"),
    "那覇": ("naha", "Naha"),
}
START_DATE = date(2016, 1, 1)
END_DATE = date(2025, 12, 31)
EXPECTED_DAYS = (END_DATE - START_DATE).days + 1  # うるう年も含む3,653日。

# 日本語の項目名と、Parquetに保存する列名・型・補助情報の接頭辞。
# タプルは、複数の値をひとまとまりにする書き方。for文で各値に分解できる。
METRICS = {
    "平均気温(℃)": ("temp_mean_c", "DOUBLE", "temp_mean", False),
    "最高気温(℃)": ("temp_max_c", "DOUBLE", "temp_max", False),
    "最低気温(℃)": ("temp_min_c", "DOUBLE", "temp_min", False),
    "降水量の合計(mm)": ("precipitation_mm", "DOUBLE", "precipitation", True),
    "日照時間(時間)": ("sunshine_hours", "DOUBLE", "sunshine", True),
    "平均湿度(％)": ("relative_humidity_mean_pct", "DOUBLE", "relative_humidity_mean", False),
}

# 1地点分の20列を、上の設定から組み立てる。
# FIELDSの1要素は「CSVの項目名、補助情報名、出力列名、SQLの型」。
FIELDS = []
for label, (value_column, sql_type, prefix, has_no_event) in METRICS.items():
    FIELDS.append((label, "", value_column, sql_type))  # 補助情報名が空の列は観測値。
    if has_no_event:  # 降水量と日照時間だけに「現象なし情報」が付く。
        FIELDS.append((label, "現象なし情報", prefix + "_no_event", "INTEGER"))
    FIELDS.append((label, "品質情報", prefix + "_quality", "INTEGER"))
    FIELDS.append((label, "均質番号", prefix + "_homogeneity", "INTEGER"))


def read_station_rows(path):
    """1ファイルを読み、地点ごとに分けた行をPythonのリストで返す。"""
    # utf-8-sigなら、UTF-8のBOM（先頭の目印）があってもなくても読める。
    # newline=''は、改行の解釈をcsvモジュールに任せるための指定。
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.reader(source))
    if len(rows) < 7:
        raise ValueError(f"{path.name}: ヘッダー6行とデータが必要です。")

    # 気象庁CSVの3行目が地点、4行目が項目、6行目が補助情報。
    # Pythonの添字は0始まりなので、3行目はrows[2]となる。
    stations, items, details = rows[2], rows[3], rows[5]
    width = len(items)
    if items[0] != "年月日" or any(len(rows[i]) != width for i in (2, 4, 5)):
        raise ValueError(f"{path.name}: 想定と違うヘッダーです。日付1列の設定を確認してください。")
    if any(rows[4]):
        raise ValueError(f"{path.name}: 比較値などの追加ヘッダーには未対応です。")

    # 「地点、項目、補助情報」の組み合わせから、列の位置を引ける辞書を作る。
    # これにより、札幌と那覇の順や項目の順が変わっても正しく読み取れる。
    positions = {}
    for index in range(1, width):  # 0列目の日付を除き、最後の列まで繰り返す。
        key = (stations[index], items[index], details[index])
        if key in positions:
            raise ValueError(f"{path.name}: ヘッダーが重複しています: {key}")
        positions[key] = index

    station_names = list(dict.fromkeys(stations[1:]))  # 重複する地点名を、元の順でまとめる。
    expected_keys = {
        (station, label, detail)
        for station in station_names
        for label, detail, _, _ in FIELDS
    }  # 集合（set）は、順番を気にせず要素の一致を調べるのに便利。
    if set(positions) != expected_keys:
        missing = expected_keys - set(positions)
        extra = set(positions) - expected_keys
        raise ValueError(f"{path.name}: 列の設定が違います。足りない列={missing}、余分な列={extra}")
    for station in station_names:
        if station not in STATIONS:
            raise ValueError(f"{path.name}: 地点「{station}」をSTATIONSに登録してください。")

    # 入力ファイル内の日付を先に検査する。観測値が欠測でも日付の行は必要。
    dated_rows = []
    seen_dates = set()
    for line_number, row in enumerate(rows[6:], start=7):
        if len(row) != width:
            raise ValueError(f"{path.name}:{line_number}: 列数が{width}ではありません。")
        try:
            day = datetime.strptime(row[0], "%Y/%m/%d").date()
        except ValueError as error:
            raise ValueError(f"{path.name}:{line_number}: 日付が読めません: {row[0]}") from error
        if day in seen_dates or not START_DATE <= day <= END_DATE:
            raise ValueError(f"{path.name}:{line_number}: 日付の重複または期間外: {day}")
        seen_dates.add(day)
        dated_rows.append((line_number, day, row))
    if len(seen_dates) != EXPECTED_DAYS:
        raise ValueError(f"{path.name}: {len(seen_dates)}日分です。{EXPECTED_DAYS}日分が必要です。")

    result = []
    for station in station_names:
        station_id, station_name = STATIONS[station]
        # 出力順に必要な列の位置を取り出し、各行で使い回す。
        indices = [positions[(station, label, detail)] for label, detail, _, _ in FIELDS]
        for line_number, day, row in dated_rows:
            values = []
            for index, (_, _, column, sql_type) in zip(indices, FIELDS):
                cell = row[index].strip()  # 前後の空白を除く。
                try:
                    if cell == "":
                        value = None  # PythonのNoneは、DuckDBではNULL（欠測）になる。
                    elif sql_type == "INTEGER":
                        value = int(cell)  # 品質情報などを整数へ変換する。
                    else:
                        value = float(cell)  # 気温・降水量などを小数へ変換する。
                        if not math.isfinite(value):
                            raise ValueError("NaNや無限大は受け付けません。")
                except ValueError as error:
                    raise ValueError(
                        f"{path.name}:{line_number}: {station}/{column}の値が不正です: {cell}"
                    ) from error
                values.append(value)
            # 1行＝1地点の1日。品質情報も原本どおり残し、ここでは除外しない。
            result.append((station_id, station_name, day, *values))
    print(f"読み込み: {path.name} → {len(station_names)}地点、{len(result):,}行")
    return result


def main():
    # 設定ミスで、異なる観測所に同じIDを付けていないか確認する。
    station_ids = [station_id for station_id, _ in STATIONS.values()]
    if len(station_ids) != len(set(station_ids)):
        raise ValueError("STATIONSの地点IDが重複しています。")

    all_rows = []
    seen_keys = set()
    for path in INPUT_FILES:
        for row in read_station_rows(path):
            key = (row[0], row[2])  # 地点IDと日付の組み合わせ。
            if key in seen_keys:
                raise ValueError(f"複数の入力ファイルに同じ地点・日付があります: {key}")
            seen_keys.add(key)
            all_rows.append(row)
    if not all_rows:
        raise ValueError("入力データがありません。INPUT_FILESを確認してください。")

    # テーブルの列名と型を組み立てる。列名は上の設定で定義したものだけを使う。
    schema = ["destination_id VARCHAR", "station_name VARCHAR", "date DATE"]
    schema.extend(f"{column} {sql_type}" for _, _, column, sql_type in FIELDS)
    con = duckdb.connect()
    try:
        con.execute("CREATE TABLE weather_daily (" + ", ".join(schema) + ")")
        # ?は値の差し込み位置。値そのものはSQLに連結せず、別の引数で渡す。
        placeholders = ", ".join(["?"] * len(schema))
        con.begin()  # トランザクションを開始し、行ごとではなく全行をまとめて確定する。
        con.executemany(f"INSERT INTO weather_daily VALUES ({placeholders})", all_rows)
        con.commit()  # 全行の追加に成功したので、変更を確定する。
        con.sql("""
            SELECT destination_id, count(*) AS days,
                   min(date) AS first_date, max(date) AS last_date
            FROM weather_daily GROUP BY destination_id ORDER BY destination_id
        """).show(max_rows=len(set(row[0] for row in all_rows)))

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        # まず一時ファイルに全データを書き、成功してから正式な名前に切り替える。
        # 途中で変換に失敗しても、前回の完成済みParquetはそのまま残る。
        with tempfile.NamedTemporaryFile(dir=OUTPUT_FILE.parent, suffix=".parquet", delete=False) as temporary:
            temporary_path = Path(temporary.name)
        try:
            con.sql("SELECT * FROM weather_daily ORDER BY destination_id, date").write_parquet(str(temporary_path))
            temporary_path.replace(OUTPUT_FILE)  # 再実行時は、この統合ファイルだけを更新する。
        finally:
            temporary_path.unlink(missing_ok=True)  # 失敗時に残った一時ファイルを片付ける。
    finally:
        con.close()
    print(f"保存しました: {OUTPUT_FILE}（{len(all_rows):,}行）")


if __name__ == "__main__":  # importしただけでは実行せず、直接起動したときに実行する。
    main()
