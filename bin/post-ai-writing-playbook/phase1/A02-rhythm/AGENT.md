# A02　文のリズムと句読法

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

M02〜M04と副指標を、文数と句読点の分母を保持して比較する。

## 入力

- T03対象・coverage
- T02 P所有ブロック・文・token・M02〜M04

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 機械文、文長と断片、隣接差、段落1文率、句読点を計数する。
2. 主指標の年等重み差、著者区間、各年の不足を保存する。
3. カンマ間隔、5個以上の補助、旧近似を別に計算する。
4. 低n、極端CV、タグなしコード候補を診断し、負例と集計を別計算で検証する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `sentence-annual.csv`
- `rhythm-contrasts.csv`
- `rhythm-diagnostics.json`
- `rhythm.svg`

## 完了条件

- C01　M02〜M04は固定Pから計算され、語なし・一文・低nが区別できる。
- C02　カンマ間隔の文ベースと旧記事近似が別列で、数字内カンマが除かれる。
- C03　著者区間と図を入力から独立に照合できる。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a02-settings.json](../references/a02-settings.json)

## 混同しないこと

- 1文のCVを0にしない。
- burstinessをCVと独立した発見にしない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
