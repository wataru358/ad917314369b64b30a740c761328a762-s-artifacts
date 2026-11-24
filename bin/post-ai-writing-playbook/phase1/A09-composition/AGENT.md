# A09　話題と書き手の入れ替わり

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

話題・長さの構成、既知著者への重み、本人内差を測る。

## 入力

- T02 metrics/metadata/記事
- T03 coverage
- A01〜A08の比較と適用範囲

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 話題×P語数帯で支持30を満たすセルと基準期固定qを凍結する。指標別cell・年・分類キーを保存する。
2. 全体と共通範囲、固定組成と同対象の無調整値を比較する。
3. 年内著者等重みと、両期間に現れる著者の年等重み本人内差を計算する。
4. 寄与分解、著者cluster区間、A04〜A08の適用範囲を保存し、固定辞書からAI話題タグと本文S語句を別々に付ける。
5. 重み、分解、区間・独立した適用範囲を元表から再計算する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `metric-support.csv`
- `weights.csv`
- `composition-contrasts.csv`
- `author-year.csv`
- `within-author.csv`
- `decomposition.csv`
- `ai-cues.csv`
- `composition.svg`

## 完了条件

- C01　指標ごとに六年の支持、共通範囲、固定重み、ESS、除外率を照合できる。
- C02　同一対象の無調整と固定構成、既知著者等重み、本人内の点差・選択率を区別する。
- C03　分解恒等式、各探索の適用範囲、タグ/本文AI語句と未知の判定を検証できる。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a09-ai-topic.json](../references/a09-ai-topic.json)
- [t02-strata-map.json](../references/t02-strata-map.json)

## 混同しないこと

- 自分自身の語数帯で層を揃えたM01は別の問い。
- 比較の支持不足を母集団に一般化しない。
- 語句露出をAI使用や意味話題の真値にしない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
