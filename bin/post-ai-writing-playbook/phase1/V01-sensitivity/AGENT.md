# V01　条件を変えた再分析

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

事前に決めた感度条件を一つずつ適用し、結論の適用範囲を確かめる。

## 入力

- A01〜A12の合格済み出力
- T00〜T03の凍結入力と特徴量
- A04重複成分

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 同梱の条件表から具体的な変種IDを固定し、各条件を一つずつ変える。
2. 部位、文境界、語形、言語、品質、話題、組成、著者、期間、日時、重複の比較を記録する。
3. 支持ゼロ・不足・必要入力の欠落を数え、実装上のfailureや残作業を別状態にする。
4. 旧結果と現比較の対象違い、A11/A12の探索と反例を独立に確認する。
5. 表・図・大偏差の元記事抜き取りを独立実行する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `variant-plan.json`
- `robustness.csv`
- `exploration-confirmation.json`
- `sensitivity.svg`

## 完了条件

- C01　予定の変種×六主指標の全セルが計算値または理由付き状態を持つ。必須未処理はない。
- C02　原比較との差・n・欠測・支持を別計算で照合し、定義上のゼロと反転を区別する。
- C03　A04境界・重複の未測定、A11・A12探索、図の反例と制約を保存する。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [v01-variants.json](../references/v01-variants.json)

## 混同しないこと

- 計算不能を影響なしとみなさない。
- 0をまたぐかだけで頑健と決めない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
