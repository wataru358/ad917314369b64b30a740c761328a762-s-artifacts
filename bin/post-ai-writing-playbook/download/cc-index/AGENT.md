# D01　Common CrawlのDEV候補を固定する

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

CC-MAIN-2025-43の公開Parquet索引から、定義に合うdev.toの候補パスと各パスの保存位置を固定する。

## 入力

- ルート設定のcrawl、seed、通信上限、pilot.cc_records
- 選んだcrawlのcc-index-table.paths.gzとsubset=warcのParquet索引

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 一覧の取得元、圧縮上限、フィルタと候補ルートの定義を固定する。保存済み一覧のハッシュを確認して再利用する。
2. キー順に必要列と範囲を読む。まず5候補を索引から読戻し、重複排除と保存位置の選択を確かめる。
3. ファイルの件数と候補を一緒に確定し、保存した一覧にある全キーの処理が終わるまで、設定の上限ごとに続ける。
4. 最も早い保存記録を固定した候補を出力する。全ファイルの完了、候補IDとパス、件数を独立検証担当が保存物から確認する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `summary.json`
- `manifest.paths.gz`
- `index-files.jsonl`
- `candidates.jsonl`

## 完了条件

- C01　保存した圧縮一覧のSHA-256がmanifestと一致し、展開して得た対象キーと処理済み索引台帳が一対一で対応する。
- C02　5候補の少数検証の記録があり、索引上のフィルタ、正規化したパス、保存位置を追跡できる。
- C03　候補行はpath順で一意。IDを再計算して全行で一致し、保存位置は日時と同順位の規則で確定している。
- C04　ファイル別件数と全体件数が一致する。索引の全ファイルを処理済みと確認し、対象範囲と歴史上の参考件数を区別して報告している。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [download-spec.md](../download-spec.md#共通の保存と再開)
- [download-spec.md](../download-spec.md#d01の候補と保存位置を固定する)

## 混同しないこと

- 200・HTMLは索引上の取得条件。記事本文、公開年、英語の採否は後で判定する。
- 索引の途中集計から全体件数を推計しない。未処理のキーを件数0に置き換えない。

引継ぎは [download-handoff.md](download-handoff.md)。状態は[status.json](status.json)。
