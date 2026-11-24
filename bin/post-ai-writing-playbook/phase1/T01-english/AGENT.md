# T01　本文言語判定と英語集合

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

全候補に状態を与え、本文の英語と公開UTC年で分析集合を固定する。

## 入力

- T00 extraction.jsonl、input-ledger.csv、pilot.jsonおよび元D02出典

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 同梱language_rules.pyをlanguage-rules.pyとして凍結し、Lingua全75言語を固定する。T00のprobe記事でS/P/Lと1200文字区間の保存と再読取を確認する。
2. 各年の校正20、検証10と別枠診断をhashで固定する。校正と診断は閾値0.70と0.30を固定する際の品質確認に使う。
3. 全候補を自動採点し、校正・診断の根拠付き全文判定だけを別列の手動補正にする。盲検検証の結果を保存する。
4. 英語状態でUTC公開年が2018〜2025の候補だけadopted=trueとする。対象外・欠時刻・mixed・空・利用不能の行を残す。
5. 独立検証で候補別ハッシュ、S区間の完全被覆とラベル、UTC年、標本・採否の集計を再計算する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `cohort.csv`
- `language-evidence.jsonl`
- `language-rules.py`
- `language-settings.json`
- `language-review.json`

## 完了条件

- C01　候補と同数の一意な言語・採否行があり、UTC境界と全状態の件数が合う。
- C02　盲検校正・検証・診断を分け、凍結順序、標本不足、手動補正の証拠を保存した。
- C03　採用対象に非英語・判定不能・期間外が流入せず、短文・同文は残る。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [language_rules.py](../references/language_rules.py)

## 混同しないこと

- html lang・CC言語・タグは判定器の代わりにしない。
- 英語主体mixedは候補に留める。
- 手動補正で検証群を底上げしない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
