# Phase 1 を再開する

現在のrunで `python3 workflow.py next` を実行する。進行中のleafがあれば、依存タスクの成果物と試行内の入力ハッシュを照合し、最後に合格した処理単位の次から再開する。同じrun・試行・コード・設定なら完成済みシャードを再利用する。入力・測定規則を変更する場合は理由と変更箇所を記録し、以前の証拠を保持した別試行で続ける。

## D02 から受け取るもの

D02の完了した試行から `acquisitions.jsonl`、`manifest.json`、`summary.json`、`verification.json` と各成功行のHTMLを読む。各行のID・path・URL・取得状態・UTC公開時刻の出典・CC収録時刻・HTMLファイルのハッシュを確認する。取得失敗行も保持する。手元の元runの件数や記事IDと一致する必要はない。

## 次のleafへ渡すもの

- T00は入力台帳と全候補の本文抽出、そのコードと抽出状態を渡す。
- T01は採否と年を含む `cohort.csv` と全候補の言語証拠を渡す。
- T02は `articles.jsonl`、`metadata.csv`、`metrics.csv`、`segmentation.py`、`fixtures.json`、`topic-map.json` を渡す。
- T03は `coverage.csv`、日付台帳、対象集計への参照を渡す。
- A04は著者の連結成分分割をA06とV01へ渡す。A07は盲検標本と非公開の対応台帳をA11へ渡す。A06・A08はDOM構造と位置の台帳をA11へ渡す。A09は指標別セルと `weights.csv` をA10・A12・V01へ渡す。

R01まで完了したら、対象・尺度・不成立の根拠を含む日本語資料と `phase2-inputs.json` を確定する。後者はD02のHTML取得台帳、T00抽出器、T01採否台帳、T02の固定コードと測定表、T03のcoverage、A09の重みを、パッケージ基準相対パス、SHA-256、各入力の試行番号、スキーマ版で指す。全量のPhase 1入力として対象、適用版、試行を明記する。 `python3 workflow.py sync` と `python3 workflow.py validate` を実行する。

再開用の記録には未完了の処理ID、最後に保存した成果物、依存ハッシュ、再開コマンド、未検証範囲を残す。支持ゼロや入力欠測が測定上の結果として確定した場合はNA行に理由を残す。依存データそのものが失われて続行できない場合は、復旧に必要なファイルと理由をstatusに記録する。
