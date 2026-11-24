# A06　見出しと冒頭・末尾

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

辞書による見出し機能、パターン集中、冒頭末尾表現を比較する。

## 入力

- T03対象
- T02見出しとS/P位置
- A04 split.csv と候補凍結証拠

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 固定見出し辞書を発見側の盲検60候補で確認し、規則と未一致を凍結する。
2. 見出しごとのSカーソル・節語数、機能列、年別集中度とサイズ調整を計算する。
3. A04群の先頭/末尾50P語を使い、2〜5語列の増減各15を窓ごとに固定して別群で検証する。
4. 原DOM順、見出し階層、同文と著者の集中、固定候補・図を独立確認する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `headings.csv`
- `heading-sequences.csv`
- `window-candidates.csv`
- `window-holdout.csv`
- `structure-summary.csv`
- `structure.svg`

## 完了条件

- C01　見出し校正・凍結・評価の順序があり、見出しなし・辞書認識なしと集中度が再計算できる。
- C02　まとめ存在、条件付き節長、S位置が各々の分母で読める。
- C03　冒頭末尾候補が検証前に固定され、全候補の検証結果と群漏れが照合される。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a06-settings.json](../references/a06-settings.json)

## 混同しないこと

- まとめ見出しが増えたことだけで構造全体が画一化したと書かない。
- 見出し辞書は意味上の正解ではない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
