"""気象庁のCP932形式のCSVを、同じフォルダにUTF-8形式で保存する。"""

import argparse  # コマンドラインで渡された引数を読み取る標準ライブラリ。
from pathlib import Path  # ファイルの場所や名前を扱うための標準ライブラリ。


def main():  # 引数の読み取りからファイル保存までの処理をまとめる。
    parser = argparse.ArgumentParser(description=__doc__)  # 冒頭の説明文をヘルプに表示する。
    parser.add_argument("source", type=Path, help="変換するCP932形式のCSVのパス")  # 必須の引数をPathとして受け取る。
    args = parser.parse_args()  # 実際に渡された引数を読み取り、args.sourceに格納する。
    source = args.source  # 入力ファイルのパスに、短い名前を付ける。
    target = source.with_name(source.stem + "_utf8" + source.suffix)  # 同じフォルダで、拡張子の前に_utf8を付ける。

    try:  # 読み取り・変換・保存の失敗を、下のexceptで受け止める。
        text = source.read_bytes().decode("cp932")  # 原本のバイト列をCP932として解読する。改行はそのまま残す。
        utf8_bytes = text.encode("utf-8")  # 解読した文字列をUTF-8のバイト列に変換する。
        with target.open("xb") as output:  # 新規ファイルとして開く。既に存在する場合は上書きせずエラーにする。
            output.write(utf8_bytes)  # UTF-8の内容を書き込む。withを抜けるとファイルは自動で閉じる。
    except (OSError, UnicodeError) as error:  # ファイル操作や文字コードの変換に失敗した場合を扱う。
        parser.exit(1, f"変換できませんでした: {error}\n")  # 理由を表示し、失敗を表す終了コード1で終了する。

    print(f"保存しました: {target}")  # 完了したことと、出力ファイルの場所を表示する。


if __name__ == "__main__":  # このファイルを直接実行した場合だけ、下の処理を呼び出す。
    main()  # 上で定義した一連の処理を実行する。
