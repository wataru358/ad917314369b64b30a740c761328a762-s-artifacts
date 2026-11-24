# A03　リスト・太字・見出し

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

構造がある記事の割合、使われる量、S上の位置を比較する。

## 入力

- T03対象・coverage
- T02記事・DOMイベント・太字・M05/M06

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 主M05/M06と構造有無・使用量、見出し密度と候補を計算する。
2. 元S語順位に基づく半分と20/60/20領域別の計数を保存する。
3. 品質候補を固定選定しraw/clean DOMに照らす。
4. 独立に位置と分母、主差・区間・図を立て直す。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `format-annual.csv`
- `format-contrasts.csv`
- `format-positions.csv`
- `format-audit.json`
- `formatting.svg`

## 完了条件

- C01　M05/M06の年等重み点差・区間、および構造の有無と条件付き強度が再計算できる。
- C02　各領域のS語・L語・太字語・太字区間のカウントが一致する。
- C03　空領域、S=0、構造なし、投影失敗と例示の役割が区別される。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a03-settings.json](../references/a03-settings.json)

## 混同しないこと

- リストがなくS語が正なら0。S語なしはNA。
- 太字区間と太字語、DOMリストとL語有無は同じ量ではない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
