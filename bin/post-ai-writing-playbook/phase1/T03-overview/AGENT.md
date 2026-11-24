# T03　対象統計と収録範囲

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

候補数・有効範囲・欠測・分布を説明する対象表と図を作る。

## 入力

- T00入力と抽出台帳
- T01 cohort.csv
- T02記事、指標、metadata

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 全候補の日時、取得、言語状態、採否を結合し、欠行と重複を検査する。
2. 採用記事のP/L/U/Sの和・中央値・分位・0を含む語数帯、日時可用性、同文・著者・タグ・組織の分母を集計する。
3. UTC年月と四半期の全格子を作り、設定と取得証拠から完結、部分、未観測、不明を割り当てる。
4. 図の実ファイルを開き、点と年ごとの分母・NAを元表から独立に照合する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `coverage.csv`
- `scope.csv`
- `date-ledger.csv`
- `word-bands.csv`
- `overview.svg`

## 完了条件

- C01　候補から採用までの記事数が保存則に合い、P/L/U/Sの語数・帯・分位を再計算できる。
- C02　8年・96月・32四半期の観測状態と部分年が明示される。
- C03　年・期間の件数と不明日付、既知著者、組織、タグ、重複の対象が区別される。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [t03-settings.json](../references/t03-settings.json)

## 混同しないこと

- 2025年の未観測月を0にしない。
- DEV全体の投稿数と呼ばない。
- 保存日の中央値を公開年に転用しない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
