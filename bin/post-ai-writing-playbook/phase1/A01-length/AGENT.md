# A01　記事と段落の長さ

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

PとSの長さと段落長を比較し、M01の主比較を作る。

## 入力

- T03 coverageと対象
- T02記事・metadata・M01
- T00抽出と固定標本の元HTML

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. P/Sの年別語数分布、帯、1〜9月補助、M01の全点・既知著者点・著者cluster区間を計算する。
2. 所有P段落の中央値、段落および記事を等重みにした分布を作る。
3. 固定年別上位長文候補と原HTMLを点検する。
4. 別式で年重み、log尺度、区間反復、図を照合する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `annual-length.csv`
- `paragraph-distributions.csv`
- `length-audit.json`
- `m01-contrast.csv`
- `length.svg`

## 完了条件

- C01　M01のlog1p年等重み点差、原語数、全記事点と著者区間を再現できる。
- C02　記事等重み段落分布と段落等重み分布が別にある。
- C03　長文診断の抽出規則と照合結果があり、0語とNAを区別する。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a01-settings.json](../references/a01-settings.json)

## 混同しないこと

- M01の原語数とlog差は交換できない。
- 記事が長いことを段落が長いことへ置き換えない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
