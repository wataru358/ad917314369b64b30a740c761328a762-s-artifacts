from pathlib import Path
import csv

# Path は Node.js の path.join() などに近い、パスを表すオブジェクト。
# この相対パスは「このファイルの場所」ではなく、コマンドを実行したディレクトリを基準に解決される。
csv_path = Path("data/interim/jma_tokyo_daily_2025_utf8.csv")

# with は TypeScript の `using` に近いコンテキスト管理構文。
# ブロックを抜けると（例外が起きた場合も）csv_file.close() が自動的に呼ばれる。
# newline="" は csv モジュール自身に改行コードを正しく処理させるための推奨指定。
# Python では波括弧ではなく、コロンの後のインデントがブロックの範囲を表す。
with csv_path.open(encoding="utf-8", newline="") as csv_file:
    # csv.reader はファイル全体を配列にするのではなく、1行ずつ返すイテレータ。
    # 各 row は、CSV の1レコードを列ごとに分割した list[str] になる。
    reader = csv.reader(csv_file)

    # range(1, 10) は 1〜9 を生成する（終端の 10 は含まれない）。
    # zip は2つのイテレータをペアにし、短い側が尽きた時点で終了する。
    # そのため、CSV が10行以上あってもここで読むのは先頭9行だけ。
    for line_number, row in zip(range(1, 10), reader):
        print(
            # :>2 は値を幅2で右寄せする f-string の書式指定。
            f"line={line_number:>2}",
            f"columns={len(row):>2}",
            # row[:8] は先頭から最大8要素を取り出すスライス（元の list は変更しない）。
            # repr() は改行や引用符なども判別しやすい、デバッグ向けの文字列表現を返す。
            repr(row[:8]),
        )
