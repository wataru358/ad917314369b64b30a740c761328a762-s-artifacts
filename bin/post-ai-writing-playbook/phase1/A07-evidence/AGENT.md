# A07　経験談と具体的な検証記述

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

固定盲検標本で内容記述を読み、全記事の機械代理との対応を調べる。

## 入力

- T03対象
- T02原DOM、文単位、元本文/metadata
- A05 voice-article.csv

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 各年を固定hashで並べ、校正4、評価16を保存する。年や著者を隠し、内容rubricと代理辞書を別々に凍結する。
2. 各年4件を抜いて別セッション用の固定packetを残す。評価全文を読み、五カテゴリに根拠・S文ID・状態・内容種別・操作modeを付ける。
3. 別セッション再評価の未開封入力、実行記録・裁定を保つ。
4. 全量25代理を固定P語句・数字・リンク・DOM規則で計測し、同一標本内のA05語形と内容対応を点検する。
5. 上限下限、各分母、記事種・年・帯、代理の不一致を集計する。別読者の根拠監査と別実装のカウント検査を行う。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `sample-manifest.json`
- `rubric.json`
- `coding-ledger.jsonl`
- `rereview.json`
- `proxy.csv`
- `correspondence.csv`
- `evidence-summary.csv`

## 完了条件

- C01　固定校正と固定評価は不交差。規則凍結後に評価記事を全文確認し、全件に根拠付き状態と範囲がある。
- C02　再評価は固定subsetを別セッションで行い、初回と再評価と裁定を保つ。
- C03　全量代理、内容標本、S/P分母、判断不能範囲、支持不足を区別できる。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a07-sample-settings.json](../references/a07-sample-settings.json)
- [a07-content-rules-v1.json](../references/a07-content-rules-v1.json)
- [a07-proxy-settings-v1.json](../references/a07-proxy-settings-v1.json)

## 混同しないこと

- 本人が実施したか、記事がそう記したか、代理が一致したかを分ける。
- 判断不能を無として加えない。
- 架空の再評価やまとめラベルで穴を埋めない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
