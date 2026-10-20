"""対応表の全対象をJMAから自動取得し、日別の品質検査まで実行する。

    uv run python download_weather_all.py

同じコマンドを再実行すると、検証済みのCSVはスキップする。
最高気温＋降水量、2016〜2025年、品質情報・均質番号付き。
2026-10-05に公式画面の公開JavaScriptと実際の応答で送信形式を確認。
これは仕様保証された公開APIではなく、公式画面のCSV取得処理を使うもの。
参照: https://www.data.jma.go.jp/risk/obsdl/web/dist/top.bundle.js
       https://www.data.jma.go.jp/risk/obsdl/web/dist/whatsnewHistory.js
"""

import argparse
import hashlib
import json
import math
import re
import socket
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# 前に作った検査コードを再利用する。新しい外部ライブラリは必要ない。
import check_weather_coverage as check

ROOT_URL = "https://www.data.jma.go.jp/risk/obsdl/"
OUTPUT_DIR = check.BASE / "data/raw/jma_daily_57_auto"
CACHE_DIR = check.BASE / "data/interim/jma_station_catalog"


def atomic_bytes(path, content):
    """完成するまで一時ファイルに置き、途中の内容を正式ファイルにしない。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
        temporary.write(content)
    try:
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def save_json(path, value):
    atomic_bytes(path, json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8"))


class JmaClient:
    """同時アクセスをせず、通信の間に待ち時間を入れる小さなクライアント。"""

    def __init__(self, interval):
        self.interval = interval
        self.last_finished = 0.0

    def post(self, endpoint, payload):
        # フォームと同じ形式で送る。日本語や記号のエスケープはurlencodeに任せる。
        request = Request(ROOT_URL + endpoint, data=urlencode(payload).encode("ascii"),
                          headers={"Content-Type": "application/x-www-form-urlencoded",
                                   "User-Agent": "JapanTravelWeatherResearch/1.0",
                                   "Referer": ROOT_URL})
        for attempt in range(3):
            pause = self.interval - (time.monotonic() - self.last_finished)
            if pause > 0:
                time.sleep(pause)
            try:
                with urlopen(request, timeout=60) as response:
                    return response.read(), dict(response.headers.items())
            except HTTPError as error:
                # 一時的なサーバーエラーだけ再試行。アクセス拒否などはそのまま停止。
                if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    raise
                retry_after = error.headers.get("Retry-After", "")
                # 長い待機を指定された場合、無理に再試行せず次回の実行に任せる。
                if retry_after and (not retry_after.isdigit() or int(retry_after) > 60):
                    raise RuntimeError(f"JMAが再試行待機を指定しました: {retry_after}") from error
                time.sleep(max(5 * 2**attempt, int(retry_after or 0)))
            except (URLError, TimeoutError, socket.timeout):
                if attempt == 2:
                    raise
                time.sleep(5 * 2**attempt)
            finally:
                self.last_finished = time.monotonic()


def resolve_station(row, client, cache_dir):
    """履歴表の5桁番号から地域を選び、画面用の取得IDを公式一覧で確認する。"""
    # 例：44132（履歴表の東京）とs47662（画面の東京）は別の番号体系。
    # 基本は履歴表番号の先頭2桁。沖縄の離島は画面では沖縄県(91)にまとめられる。
    region = row["観測所番号"][:2]
    if not re.fullmatch(r"\d{2}", region):
        raise ValueError(f"観測所番号が不正です: {row['観測所番号']}")
    if row["都道府県"] == "沖縄県":
        region = "91"  # 公式region_91一覧に石垣島・宮古島が含まれることを確認済み。
    cache = cache_dir / f"region_{region}.json"
    if cache.exists():
        catalog = json.loads(cache.read_text(encoding="utf-8"))
    else:
        raw, _ = client.post("top/station", {"pd": region, "format": "json"})
        catalog = json.loads(raw)
        if "markers" not in catalog:
            raise ValueError(f"地域{region}の地点一覧の形式が変わっています。")
        save_json(cache, catalog)
    # 地図には同じ地点の文字とアイコンがあるので、stidをキーにして重複を除く。
    matches = {m["stid"]: m for m in catalog["markers"]
               if m.get("kind") == "station" and m.get("stname") == row["気象庁の観測所"]
               and not m.get("ended")}
    if len(matches) != 1:
        raise ValueError(f"{row['気象庁の観測所']}: 現行の観測所を一意に特定できません。")
    marker = next(iter(matches.values()))
    # 同名の別地点を選ばないように緯度経度も照合する。
    latitude = re.search(r"北緯：(\d+)度([\d.]+)分", marker["title"])
    longitude = re.search(r"東経：(\d+)度([\d.]+)分", marker["title"])
    if not latitude or not longitude:
        raise ValueError(f"{marker['stname']}: 地点一覧の緯度経度を読み取れません。")
    lat = int(latitude[1]) + float(latitude[2]) / 60
    lon = int(longitude[1]) + float(longitude[2]) / 60
    # 数kmの照合に使う近似距離。移転を補正したり、系列を接続したりはしない。
    distance = math.hypot((lat - float(row["観測所緯度"])) * 111,
                          (lon - float(row["観測所経度"])) * 111 * math.cos(math.radians(lat)))
    if distance > 5:
        raise ValueError(f"{marker['stname']}: 対応表の位置と約{distance:.1f}km離れています。確認が必要です。")
    return marker


def make_payload(station_id):
    # 公式画面のコードで確認した要素番号：202=最高気温、101=降水量の合計。
    # 地点ごとに10年を取得するので、利用者による地域分割は不要。
    # 1要求は2項目×3,653日。画面のデータ量上限200,000より十分小さい。
    return {
        "stationNumList": json.dumps([station_id]),
        "aggrgPeriod": "1",  # 日別値。
        "elementNumList": json.dumps([["202", ""], ["101", ""]]),
        "interAnnualType": "1",  # 連続期間。
        "ymdList": json.dumps(["2016", "2025", "1", "12", "1", "31"]),
        "option": json.dumps({"list": ["obs"], "nyear": 0}),
        "downloadFlag": "true", "rmkFlag": "1", "disconnectFlag": "1",
        "youbiFlag": "0", "fukenFlag": "0", "kijiFlag": "0", "csvFlag": "1",
        "jikantaiFlag": "0", "jikantaiList": "[]", "ymdLiteral": "1",
    }


def validate_csv(path, row):
    # 品質が悪い日も原本に残す。取得成功と「全日正常値」は別に判断する。
    name = row["気象庁の観測所"]
    observations, outside = {}, {}
    check.scan_file(path, {name: row}, observations, outside)
    if set(observations.get(name, {})) != check.EXPECTED or outside:
        raise ValueError(f"{path.name}: 2016〜2025の3,653日が正しくそろっていません。")


def download_one(row, marker, client, output_dir):
    number = row["観測所番号"]
    if not re.fullmatch(r"\d{5}", number):
        raise ValueError(f"観測所番号が不正です: {number}")
    target = output_dir / f"jma_{number}_daily_2016_2025.csv"
    sidecar = target.with_suffix(".request.json")
    payload = make_payload(marker["stid"])
    if target.exists():
        # 再開時は、名前だけでなく内容・送信条件も確認してスキップする。
        validate_csv(target, row)
        if not sidecar.exists():
            raise ValueError(f"{target.name}: 取得記録がありません。別フォルダへ移して再実行してください。")
        record = json.loads(sidecar.read_text(encoding="utf-8"))
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if record.get("payload") != payload or record.get("sha256") != digest:
            raise ValueError(f"{target.name}: 取得記録と内容が一致しません。")
        return "取得済み"
    raw, headers = client.post("show/table", payload)
    disposition = next((v for k, v in headers.items() if k.lower() == "content-disposition"), "")
    if not disposition.lower().startswith("attachment"):
        raise ValueError("CSVのダウンロード応答ではありません。サイトの仕様や混雑状況を確認してください。")
    # HTMLやエラーメッセージをCSVとして保存しないよう、一時ファイルで検査する。
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output_dir, suffix=".part", delete=False) as temp:
        temporary = Path(temp.name)
        temp.write(raw)
    try:
        validate_csv(temporary, row)
        record = {"url": ROOT_URL + "show/table", "payload": payload,
                  "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
                  "sha256": hashlib.sha256(raw).hexdigest(), "station": marker,
                  "mapping_station_number": number}
        save_json(sidecar, record)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return "新規取得"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", type=Path, default=check.MAPPING)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--interval", type=float, default=3, help="通信間隔（秒、最低3秒）")
    parser.add_argument("--limit", type=int, help="動作確認用。先頭の指定地点数だけ取得")
    args = parser.parse_args()
    if args.interval < 3 or not math.isfinite(args.interval) or (args.limit is not None and args.limit < 1):
        parser.error("intervalは3以上、limitは1以上にしてください。")
    try:
        _, allowed = check.read_mapping(args.mapping)
        stations = list(allowed.values())
        if args.limit is not None:
            stations = stations[:args.limit]
        client = JmaClient(args.interval)
        for i, row in enumerate(stations, start=1):
            print(f"[{i}/{len(stations)}] {row['気象庁の観測所']}を確認…", flush=True)
            marker = resolve_station(row, client, CACHE_DIR)
            state = download_one(row, marker, client, args.output_dir)
            print(f"  {state}: {marker['stid']} / 3,653日", flush=True)
        # 取得後に検査を自動実行。未取得や対象外も含む60行の対応表を出す。
        check.run(args.mapping, args.output_dir,
                  check.BASE / "data/processed/coverage_daily_check_auto.csv")
    except (ValueError, KeyError, OSError, RuntimeError) as error:
        parser.exit(1, f"停止しました: {error}\n取得済みファイルは残っています。同じコマンドで再開できます。\n")


if __name__ == "__main__":
    main()
