# A10　変化が始まった時期

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

支持診断後に固定境界、偽境界、探索折点、外挿の限界を報告する。

## 入力

- T03 coverage/date-ledger
- T02六指標と著者
- A09 weights.csv・支持と対象

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 年・月・四半期、1〜9月補助の格子と対象を作る。支持診断は値を見る前に固定する。
2. 支持した窓に季節と実暦tを含む固定回帰を当て、2022年11〜12月の扱いと暦HACを検証する。
3. 事前傾向照合と2020/21偽境界、同月の構成比較を実行し、不成立行も保存する。
4. 0/1折点で全候補BIC、連続ブロック再抽出、安定基準を計算する。
5. 欠測ありの合成データと連続例で係数、HAC、候補マスク、反復の一部または全量、図を独立検証する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `time-grid.csv`
- `support.csv`
- `time-models.csv`
- `break-candidates.csv`
- `block-replicates.csv`
- `time-stability.csv`
- `time.svg`

## 完了条件

- C01　全期間格子、支持窓、非支持理由、季節性、対象/固定qのマスクを再現できる。
- C02　固定境界、事前点検、両偽境界、候補BICとブロック再抽出の状態・失敗IDがある。
- C03　暦ラグHACと数値、図点、停止条件を独立計算で確認する。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a10-methods.json](../references/a10-methods.json)

## 混同しないこと

- S02相当の支持表を推定済みと扱わない。
- 行番号で欠測月を詰めない。
- 2023年から六指標一斉、反実仮想、AI因果を主張しない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
