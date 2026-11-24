# T02　分割・特徴量・メタデータ

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

同じ本文投影から語・文・太字・見出し・メタデータを測り、六主指標と副指標を凍結する。

## 入力

- T01 cohort.csv、language-review
- T00 extraction.jsonl と frozen extract.py
- D02保存HTML

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 同梱segmentation.pyと固定対照を保存し、P/L/U単位・所有ブロック・文・語をUnicodeオフセットで投影する。
2. 5候補から採用分を試し、採用例不足は合成fixtureで補う。固定標本を年を伏せて読み、文境界、語、組織と著者の根拠を診断する。
3. SHA確認の済んだ採用全記事で元DOM順とS語を照合し、H、太字、リスト、コード位置、六主指標、MATTR等の副指標を保存する。
4. t02_metadata_v2.pyの規則で単一数値著者、タグ、組織、種別cueと出典を保存する。t02-strata-map.jsonをtopic-map.jsonとして凍結する。
5. 別検証でID集合、語種、owner→sourceの半開区間、M01〜M06、太字・リンク位置、メタデータ矛盾、NA理由を再構成する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `articles.jsonl`
- `metadata.csv`
- `metadata-provenance.jsonl`
- `metrics.csv`
- `secondary-metrics.csv`
- `segmentation.py`
- `fixtures.json`
- `topic-map.json`
- `calibration.json`

## 完了条件

- C01　採用記事1件につき記事とmetadataが一行、主指標が六行ある。
- C02　S=P+L+U、文・語オフセット、太字重複除去と分母、既知著者IDが独立読取と一致する。
- C03　合成例・固定標本・v2メタデータの根拠を検査し、0、NA、使用なし、投影失敗を区別する。
- C04　下流側が固定コード・fixtureとデータスキーマを再利用できる。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [segmentation.py](../references/segmentation.py)
- [t02_structure.py](../references/t02_structure.py)
- [t02_controls.json](../references/t02_controls.json)
- [t02-strata-map.json](../references/t02-strata-map.json)
- [t02_metadata_v2.py](../references/t02_metadata_v2.py)

## 混同しないこと

- SをPに置き換えない。
- 組織handleは著者IDではない。
- インラインコードをS語に再挿入しない。
- 片方の構造投影失敗を全指標へ伝播させない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
