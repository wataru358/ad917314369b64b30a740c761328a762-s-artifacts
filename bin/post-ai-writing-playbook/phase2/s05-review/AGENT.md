# P2-S05　18項目の算術と主張の範囲を検証する

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

保存値に対し、測定と比較が支える範囲を判断する。判断と根拠を追跡可能にする。

## 入力

- S04の比較、記事値、判定、分母、診断と独立readback
- S03の対象、設定、標本、入力ハッシュ

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 対象manifestと比較の全キーを照合する。再利用したS04の検算と、この工程で実施した照合を区別する。既存比較から分母・月支持・有効反復・補正・NA理由を取り出す。
2. 固定感度を全行つないで、方向、母集団変更、支持不足、適用外を区別する。品質標本のbaseline・表示エラー・広告・署名×M6も理由付きで残す。
3. 合議参照の有無、分割の手数え差、太字の出典、V03/X01/X03の正負支持を確認する。X02は固定標本のE/G別に、有無、語率、判定可能数、一致・κ、不明範囲を点検する。
4. VのF/R/A、著者実数、Q、条件非再現を確認する。C01は元尺度4点の外挿、範囲外、backtest、感度を照合する。取得・生存・編集・話題差が残る箇所を示す。
5. 18項目を限定採用、保留、判断不能から根拠で決める。観測された自動値と測定妥当性を分け、各項目に許容文と証拠の位置を付ける。別担当が根拠と記述を検証する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `item-decisions.json`
- `robustness.tsv`
- `evidence-index.json`
- `independent-review.json`

## 完了条件

- C01　M6、V01/V02とV03の5系列、X01、X02 E/G、X03、C01の18判断が重複なくあり、全比較キーと固定感度へたどれる。
- C02　各判断の数値、分母、不確かさ、内容検証、代替説明、許容文がそろう。NAとunknownの両方に理由が読める。
- C03　X02の固定標本差・unknown範囲、V02条件未達、品質24比較、C01の6指標とbacktestが脱落しない。
- C04　独立担当が保存値と記述を照合し、指摘・修正・再検証を保存する。終了は全項目を確認し判断を残したことを示す。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [comparisons.md](../comparisons.md)
- [phase2-handoff.md](../phase2-handoff.md)
- [measurement-spec.md](../measurement-spec.md)

## 混同しないこと

- 元runの限定採用2、保留14、判断不能2は履歴。新runの判断の割当には使わない。
- 全compute・bootstrapの再実行は、既存照合で足りない具体的な不一致の調査に限る。

引継ぎは [phase2-handoff.md](phase2-handoff.md)。状態は[status.json](status.json)。
