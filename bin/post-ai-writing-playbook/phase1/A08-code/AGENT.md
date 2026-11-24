# A08　コードと近接散文

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

コード量・言語ラベル・見出し内の前後散文を別々に測る。

## 入力

- T03対象
- T00抽出body_html
- T02 S語、DOMイベント、metadata

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 固定12例でpre、highlight、inline、未知言語ラベル、隣接コード、見出し境界を確認する。
2. 全記事のブロックとinline量、明示クラス、状態を保存する。
3. 同一区間の前後散文を対応付け、元Sと照合し、再利用フラグを付ける。
4. 同梱の集計・区間閾値で計算し、元HTML・分母・位置・図を独立照合する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `code-events.csv`
- `code-article.csv`
- `code-annual.csv`
- `code-contrasts.csv`
- `code-audit.json`
- `code.svg`

## 完了条件

- C01　ブロックとinlineの二重計数がなく、元順序と前後対応、状態ごとの分母を復元できる。
- C02　12例の固定診断があり、0と非対応と投影失敗を判別する。
- C03　全22指標の集計と指定12の区間、層別の不成立が残る。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a08-code-rules.md](../references/a08-code-rules.md)
- [a08-aggregation.json](../references/a08-aggregation.json)

## 混同しないこと

- コードありとblockあり、可視文字比とS語数あたり文字長は区別する。
- 言語不明を推定で埋めない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
