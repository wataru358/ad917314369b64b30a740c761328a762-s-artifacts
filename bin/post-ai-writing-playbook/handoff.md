# 親担当の引継ぎ

新しい再現実行はまだ始めていない。入口はSTART.md。configのrun_idは未設定で、27末端はすべてnot_started。

最初はselftestとvalidate、次にinitとnextを実行する。以後はworkflow.py nextのresume/readyを読み、末端の引継ぎと実際の保存物で続きを決める。

## 実行後に追記するもの

run_id、configと仕様の固定hash、現在の担当とattempt、完了・未完了・阻害、次の一操作。過去の統計的判断と新しいrunの判断は別に残す。
