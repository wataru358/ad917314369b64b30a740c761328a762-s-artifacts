# R01　日本語の執筆材料

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

比較と探索を検証済みの日本語執筆材料にまとめ、Phase 2へ固定入力を渡す。

## 入力

- T03の対象とcoverage
- A01〜A12とV01の元表、図、manifest、verification
- T00/T01/T02/A09の入力資産

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 対象・主比較・具体的材料・位置・構造と文体・反例・限界を日本語で記す。
2. 方向未指定の二指標、結果前固定時刻、著者区間の別対象、p/Holmの実行状態を照合する。
3. 主張台帳と元表index、保留の理由、比較集合ごとの限界を保存する。
4. 図を開いて値・n・期間・区間の説明を突合する。
5. D02、T00抽出器、T01採否と検出器、T02語文・metadata・topic-map、T03 coverage、A09固定qをphase2-inputs.jsonに登録する。
6. 独立レビュアーが事実・計測・図・ハッシュと相対参照を点検する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `primary-metrics.csv`
- `claims.csv`
- `figure-captions-ja.csv`
- `source-result-index.csv`
- `phase2-inputs.json`

## 完了条件

- C01　六主指標の尺度、元表、記事と既知著者の点、区間対象、比較年と未実行検定の表示が一致する。
- C02　主張と保留が元表行・分母・反例・不足へ追跡でき、既存図を実際に開いて照合した。
- C03　Phase 2の必要入力参照がパッケージ相対パスとハッシュで解決し、必須未解決事項はない。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)

## 混同しないこと

- 旧runの採用22件と保留4件は期待値ではない。
- 日本語草稿の代筆、英訳、公開は別作業。
- 関連の裏付けがない異なる集合の結果を結ばない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
