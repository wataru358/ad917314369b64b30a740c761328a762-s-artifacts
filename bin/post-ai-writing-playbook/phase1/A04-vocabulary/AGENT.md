# A04　語彙の発見と検証

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

著者と完全一致Pをまたがせず、固定語句候補の年代差を再検証する。

## 入力

- T03対象
- T02元P文・所有単位・token、L/H、MATTR、metadata

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 非空Pハッシュと既知著者の連結成分を作り、固定seedハッシュで分ける。
2. 同梱条件で1〜5語の全候補を発見群内で計数し、増減・以前はまれ・固定監視語を凍結する。
3. 検証群を開き、候補の差・比・方向・再到達と成分cluster区間を計算する。P/L/Hと群を別にする。
4. 著者への広がり、話題/語数帯、年別MATTR、編集時点とinlineコード境界の限界を保存する。
5. 独立に漏れ、選定順位、分母、語境界と検証行を照合する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `split.csv`
- `candidates.csv`
- `candidate-freeze.json`
- `holdout.csv`
- `vocabulary-spread.csv`
- `mattr.csv`
- `vocabulary-audit.json`

## 完了条件

- C01　発見側と検証側の既知著者および完全一致の非空Pハッシュは交差0。
- C02　候補hashは検証結果を開く前に固定され、全採否と未再現を保持する。
- C03　元単位・文・非語境界、0語P分母、レア判定、監視語、MATTR窓不足を別実装で照合できる。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a04-settings.json](../references/a04-settings.json)

## 混同しないこと

- 点差の同方向は有意差ではない。
- 候補数を埋めるために閾値を下げない。
- P完全一致を近似重複へ外挿しない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
