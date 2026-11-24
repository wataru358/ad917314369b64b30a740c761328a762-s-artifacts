# T00　入力と実行条件を固定

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

候補集合、元HTML、抽出規則、実行環境を固定し、全候補の抽出台帳を作る。

## 入力

- D02 acquisitions.jsonl、manifest、summary、verification、成功行のHTML

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. D02の合格済み試行へ読み取り専用で接続し、候補ID・URL・日付・HTML参照と出典を台帳に写す。
2. 同梱の抽出器をextract.pyとして凍結し、Python、lxml、libxmlとロケール・UTC設定、依存導入手順を記録する。
3. D02固定5候補で小規模抽出し、body selectorと元HTML対応を独立確認する。
4. 同じコードで全候補を抽出する。成功、取得失敗、本文欠落・曖昧、復号・解析失敗を記録し、空Sは成功内に残す。
5. 入力とシャードのSHA-256、一意性、ID集合、境界ケースを別実装で判定する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `input-ledger.csv`
- `extraction.jsonl`
- `extract.py`
- `environment.json`
- `pilot.json`

## 完了条件

- C01　候補IDは一意で、全取得状態とHTMLハッシュがD02と一致する。
- C02　5候補probeと合成負例で取得失敗・抽出失敗・空Sを区別できる。
- C03　全候補の抽出状態があり、不明の捨て行がない。コード・環境・設定のSHA-256を再照合できる。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [article_extraction.py](../references/article_extraction.py)

## 混同しないこと

- 固定件数や旧run IDを採否に使わない。
- 候補失敗を欠行にしない。
- 5件で止めた試行は完了にしない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
