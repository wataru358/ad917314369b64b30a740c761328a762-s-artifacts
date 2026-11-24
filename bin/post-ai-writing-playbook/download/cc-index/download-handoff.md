# D01 の引継ぎ

初期状態は未着手。過去の研究の完了を引き継いだものではない。

最初の操作は、この末端のAGENT.mdとstatus.jsonを読み、ルートで `python3 workflow.py start D01 --owner <担当ID>` を実行すること。依存が未完了なら先行作業へ戻る。

中断時はmanifest.paths.gzのハッシュと最初の未処理キーを残す。完了後はD02へcandidates.jsonlとmanifest.jsonを渡す。

## 再開記録

実行した担当がここへ追記する。担当ID、run_id、attempt、出力先、固定入力とhash、checkpoint、完了した操作、未完了、阻害、次の一コマンドを残す。同じattemptへ戻るときは進捗を消さず追記する。
