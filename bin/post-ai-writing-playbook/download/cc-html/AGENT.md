# D02　Common CrawlのWARCと生HTMLを保存する

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

D01で固定した全候補について指定範囲のWARCを取得し、HTMLの元バイト列と成功・失敗を候補単位で残す。

## 入力

- 同じrun_idで完了したD01のoutput_dir
- D01の候補とmanifestのハッシュ
- ルート設定のseed、通信上限、pilot.cc_records

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. D01の確定成果物を照合し、seedで全候補の処理順を決める。同じ候補IDをファイル名に使う。
2. 先頭5件を試行し、HTTP 206と受信長、WARCとHTMLの検証・保存を確認する。
3. 処理待ちの候補を1件ずつ取得する。通信、WARC保存、HTML保存、台帳の順に進め、止まった区切りの次から再開する。
4. 再試行対象を上限と待機期限に従って処理する。失敗を残したまま全候補の結果を確定する。成功件数と失敗理由の内訳を報告し、生データと台帳を照合する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `summary.json`
- `acquisitions.jsonl`
- `attempts.jsonl`

## 完了条件

- C01　D01の全候補に固定順の台帳行が1つずつあり、候補の補充や欠落がない。完了行はsucceededまたは理由付きfailed。
- C02　先頭5件で範囲取得、圧縮の検証、元HTMLの保存と読戻しを確認した記録がある。
- C03　成功時は入力位置、受信長、WARCのURL・型・内部200、HTMLとWARCのハッシュを照合できる。公開日時、クロール日時、保存日時を別項目に保持している。
- C04　失敗理由、試行履歴、再試行上限、待機期限が台帳に残る。件数合計と保存済みファイルのハッシュを独立検証担当が確かめている。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [download-spec.md](../download-spec.md#共通の保存と再開)
- [download-spec.md](../download-spec.md#d02の指示範囲からwarcとhtmlを保存する)

## 混同しないこと

- Rangeの206と保存ページの200を別に記録する。
- WARC-Dateは公開日ではない。元ページにある公開日時と取得時刻を残す。
- 同じURLのライブ本文、別の保存時点、別候補で失敗を埋めない。

引継ぎは [download-handoff.md](download-handoff.md)。状態は[status.json](status.json)。
