# P2-S01　比較と収録の実行計画を固定する

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

二つの取得経路から、固定UTC月窓の比較に必要な入力と実行順を確定する。

## 入力

- R01の検証済みphase2-inputs.jsonと索引先
- D03の検証済みplan.jsonl、responses.jsonl、保存HTMLと原応答
- 固定測定仕様と設定

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. R01とD03の受理済みreceiptの出力先を開く。必要列、正規化したパス、本数とID対応を検証する。公開UTC、取得日時、CC capture、編集日時を別項目にする。
2. Phase 1との対象・定義差を記録する。旧の採否を固定し、旧2018〜2022年と新2026年の共通UTC1〜10月を主対象にする。
3. 収録、採否、測定仕様固定、D候補固定、H、独立検算、18項目判断、資料化の順序と閲覧制限をplan.jsonに記録する。正当な0と欠測を分ける。
4. 抽出pilotは固定planの先頭50件を通常例にする。コード、表、引用、入れ子リスト、埋め込み、カード、短文、警告、空、Markdownのみ、解析失敗の各最大2件をSHA256(42:phase2-extraction:<分類>:<記事ID>)順に選ぶ。重複IDは1件にまとめて選択理由を併記する。
5. 言語pilotは構造診断を精度標本と分ける。先頭50件を校正、既選択を除いた計画順で各月5件を確認とする。ラベルを先に封印し、スコアは後から開く。元の50/19/50は履歴とする。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `input-index.json`
- `plan.json`
- `pilot-plan.json`

## 完了条件

- C01　R01とD03のreceipt、入力パス、ハッシュ、必要列、結合キーを照合し、全入力と例外を列挙する。
- C02　主対象、全60年月セル、重み、D/H、盲検、比較、検証、資料の順序と定義版を固定する。
- C03　抽出・言語pilotの選択、閲覧順、標本不足、全量との違いを記録する。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [settings.json](../settings.json)
- [comparisons.md](../comparisons.md)

## 混同しないこと

- 取得経路と時期が重なる。APIとCCの網羅性を同等とみなさない。
- pilotは小規模の品質確認。fullの採否と比較には全入力での検証が要る。

引継ぎは [phase2-handoff.md](phase2-handoff.md)。状態は[status.json](status.json)。
