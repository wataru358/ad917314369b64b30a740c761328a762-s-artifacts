# A12　文体距離と分布の偏り

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

六指標の分布変化と、書式・語り口別の固定基準距離を測る。

## 入力

- T02主指標・見出し密度とP文
- A05人称と短縮形
- A09話題・P帯・対象表
- T03 coverage

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 六指標の年別分位、使用ゼロ割合、基準閾値両端と同値を作る。
2. 完全ケースの基準期経験CDFで固定midrankを計算し、組・定数・欠損を切り分ける。
3. 各組各層で共通支持を測り、別著者ペアを均一に抽出して距離を集計する。
4. 著者ペアを先に選ぶ副抽出と、保存文の完全一致共有を診断する。
5. 別実装で基準CDF、重み、選択ペア、分母・図を照合する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `quantile-shifts.csv`
- `fixed-reference.json`
- `pair-ids.csv`
- `style-distance.csv`
- `sentence-sharing.csv`
- `style.svg`

## 完了条件

- C01　基準期年等重みCDF、分位と同点が再現できる。
- C02　各組の完全ケース・共通層・固定重み、別著者のseed付きペアIDと距離を照合できる。
- C03　原尺度、端値、未知種別、対象率、著者等重み、同文診断とペア依存を明記する。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a12-distance.json](../references/a12-distance.json)

## 混同しないこと

- 同じ記事・著者を共有するペアを独立nにしない。
- 二つの距離を単一AIスコアにしない。
- unknown層の結果を全記事へ広げない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
