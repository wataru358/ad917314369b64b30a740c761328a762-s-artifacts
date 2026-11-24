# P2-S03　対象、測定仕様と著者分割を固定する

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

S04で使う共通月、固定仕様、著者分割と確認標本を結果開示前に確定する。

## 入力

- S02の英語集合、records、manifest
- S01が索引したR01の採否、構造、語・文実装、タグ
- 固定仕様と設定

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 受理済みrunからパスを解決し、設定と入力ハッシュを保存する。共通UTC月を抽出し、日付不明などを理由付きで台帳へ残す。
2. 旧CCと新APIの記事ID領域を分ける。単一の既知数値著者だけ両経路で統合する。年月別対象、著者、タグ、edited_at、取得日時、capture時刻の欠測を照合する。
3. 固定SとP/Lの順序から非空完全一致word列を作る。著者の連結成分の最小キーを使い固定SHA256 parityでD/Hを付ける。Hの語彙比較は開かない。
4. X02の校正は旧2枠/年月、新10枠/月、確認は旧12、新30を選ぶ。固定saltを使い著者内1記事。別にX02標本を除いて各経路50校正、100確認を選ぶ。IDとblind ID対応を隔離する。
5. 固定した語・文規則を取り込み、合成小例でapostrophe、Unicode・URL、fragment、P/L、太字区間、0とNA、重み、区間不足を確かめる。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `fixed-cohort.jsonl`
- `metadata-audit.json`
- `settings.resolved.json`
- `author-split.jsonl`
- `samples.jsonl`
- `fixtures.json`

## 完了条件

- C01　旧の採否、新の英語ID、60セルごとの実測数、対象外の理由を元の入力から検証できる。
- C02　著者と非空完全同文による連結成分がD/Hをまたがない。未知著者、成分サイズ、セル支持を出し、近似群の越境をS04の診断へ渡す。
- C03　X02と自動定義標本を分け、D/H別の枠、選択、salt、不足、本文ハッシュが固定される。
- C04　旧Phase 1と異なる6指標の分母とNA、語彙境界、太字投影、重み、bootstrapの小例を確認する。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [settings.json](../settings.json)
- [comparisons.md](../comparisons.md)

## 混同しないこと

- S03では仕様を固定し、Hの結果値は見ない。
- 経路間で記事IDの数値を結合しない。handleと組織IDは個人著者の代用にしない。

引継ぎは [phase2-handoff.md](phase2-handoff.md)。状態は[status.json](status.json)。
