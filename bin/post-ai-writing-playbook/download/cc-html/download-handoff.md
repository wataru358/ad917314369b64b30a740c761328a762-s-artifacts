# D02 の引継ぎ

初期状態は未着手。過去の研究の完了を引き継いだものではない。

最初の操作は、この末端のAGENT.mdとstatus.jsonを読み、ルートで `python3 workflow.py start D02 --owner <担当ID>` を実行すること。依存が未完了なら先行作業へ戻る。

再開時はnot_beforeと未処理のordinalを確認する。成功した取得証拠と失敗を含む全行をPhase 1のT00へ渡す。

## 再開記録

実行した担当がここへ追記する。担当ID、run_id、attempt、出力先、固定入力とhash、checkpoint、完了した操作、未完了、阻害、次の一コマンドを残す。同じattemptへ戻るときは進捗を消さず追記する。
