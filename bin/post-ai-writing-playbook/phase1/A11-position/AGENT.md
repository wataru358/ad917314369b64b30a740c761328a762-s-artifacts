# A11　具体的な材料までの位置

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

全記事の機械的位置と、固定評価標本の題名に対応する材料位置を測る。

## 入力

- T02 S語とDOMの対応
- A06 headings.csv
- A07固定評価と校正
- A08 code-events.csv

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 校正標本から候補辞書・タイトル対応rubricを固定する。A06/A08のDOM位置とS語をつないで全記事の機械初出を保存する。
2. A07評価標本を年伏せで全文読解し、題名に対応する最初の材料と根拠のS/DOM範囲を記録する。
3. 固定32件を独立したトップレベルセッションで再評価し、初回を伏せ、差分を裁定する。
4. 固定層の各年ペアで有無30・位置20の支持条件を適用し、内容の不成立も残す。
5. 独立の原文再読、位置再計算、誤位置・S=0の負例、図値を検証する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `structure-position.csv`
- `position-rubric.json`
- `coded-position.jsonl`
- `rereview.json`
- `position-comparisons.csv`
- `position-correspondence.csv`
- `position.svg`

## 完了条件

- C01　全採用記事でSカーソルの一致、四機械候補の位置、0/なし/入力欠落/割合NAが区別できる。
- C02　A07固定標本全件に題名の約束、根拠範囲、S外錨または不成立理由があり、別セッション再評価・裁定を保存する。
- C03　機械と内容の対応、層別のnと支持、反例、実際の図の照合がそろう。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a11-candidate-dictionary.json](../references/a11-candidate-dictionary.json)
- [a11-rubric.md](../references/a11-rubric.md)

## 混同しないこと

- 歴史runの38,980件は機械、128件は内容。その範囲を混ぜない。
- 短い位置は読書時間や質の根拠ではない。
- 同じ会話の別ワーカーを別セッションと呼ばない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
