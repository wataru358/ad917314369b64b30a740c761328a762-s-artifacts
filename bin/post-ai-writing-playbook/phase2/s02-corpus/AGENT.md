# P2-S02　新集合の全文採否を固定する

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

固定planの全IDに結果を付け、採用した2026年の英語IDと抽出本文を確定する。

## 入力

- S01のinput-index.json、plan.json、pilot-plan.json
- 索引されたD03原応答、HTML、Markdown
- 索引されたT00抽出規則、T01言語規則

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 固定plan順で原応答のID、UTC、hashを照合する。HTMLから旧と同じ抽出器でP/L/U、本文順、見出し、太字、DOM対応、警告を保存する。失敗した記事も理由付きで記録する。
2. 固定のpilotを実行する。180文字未満の構造診断やMarkdownのみを採用除外条件にしない。Markdownの無断代用を避ける。
3. 旧機械規則でS、P、L、Sの1,200文字区間を採点する。スコアと分けて、機械状態にかかわらず全件のSを内容で読む。既確認のpilot行は同一本文hashを確認して再利用する。残りは最大25件ずつ進める。
4. 全文を読み、本文ラベルと証拠を封印する。その後、対応スコアだけを開く。バッチの範囲、時刻、判定担当、ハッシュを索引にする。確認後に閾値を変えない。
5. 混在・不明を保留とし、非英語、本文なし、取得不能を分ける。広告、短さ、技術性は除外条件にしない。訂正は根拠、日時、開示済みフラグ、原記録hashとともに追記する。
6. 全件の採否と構造、planと原応答の結合を独立に確認する。既存runと同じ入力を使ったか、再収録・再判定したかを報告する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `records.jsonl`
- `decisions.jsonl`
- `english.jsonl`
- `summary.json`
- `language-review-index.json`

## 完了条件

- C01　全plan IDが計画順にrecordsとdecisionsへ1回ずつ現れ、状態別件数が総数と一致する。
- C02　英語集合が台帳のaccept_englishと一致する。保留、本文なし、取得不能は台帳に残る。
- C03　本文と根拠を原応答へ戻せる。ラベルの封印後に対応スコアを開示した証拠と、原判断を保つ訂正記録が読める。
- C04　校正、診断、未使用確認、全件の範囲を区別し、独立確認が実物の抽出位置・結合・採否・来歴を照合する。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [settings.json](../settings.json)
- [comparisons.md](../comparisons.md)

## 混同しないこと

- 抽出Sの言語と元記事全体の言語は別の範囲。
- 元runの8,942採用、220保留、7訂正は比較用の履歴。

引継ぎは [phase2-handoff.md](phase2-handoff.md)。状態は[status.json](status.json)。
