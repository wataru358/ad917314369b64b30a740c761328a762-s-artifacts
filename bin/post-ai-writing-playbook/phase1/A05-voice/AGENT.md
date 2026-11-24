# A05　書き手の声と呼びかけ

[ルート規則](../../AGENT.md)と[枝の規則](../AGENT.md)を読んでから、この末端を進める。

## 目的

Pの代名詞、短縮形、接続表現、句読記号を辞書で測る。

## 入力

- T03対象
- T02 P単位、文、token、author ID

上流の実ファイルはworkflow.pyが返すupstreamのoutput_dirとmanifestから解決する。旧チャットの絶対パスを入力にしない。

## 手順

1. 同梱辞書を凍結してP内の語形・句とP段落冒頭を走査する。
2. 年・期間・語数帯別の使用割合、千P語の密度、条件付き密度、記事語数0の状態を集計する。
3. 固定抜粋でUS、we、you、引用、短縮形の解釈を点検する。
4. 辞書マッチと分母・クラスタ再抽出・図の数字を別実装と照合する。

## 必要な出力

すべてstartが返すoutput_dirの中へ保存する。
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `voice-article.csv`
- `voice-annual.csv`
- `voice-contrasts.csv`
- `voice-audit.json`
- `voice.svg`

## 完了条件

- C01　全記事の語形計数、使用記事率、全記事と使用記事の密度の分母が別に出る。
- C02　曖昧な人称と短縮形を盲検抜粋で点検し、辞書は結果前に固定される。
- C03　単数一人称と短縮形の千P語値をT02 IDへ一意に戻せる。

完了前に、別担当が保存物と定義を独立確認する。receiptの基準・成果物・hashを確認し、ルートからworkflow.py finishで反映する。pilotだけでは完了しない。

## 参照する固定規則

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a05-settings.json](../references/a05-settings.json)

## 混同しないこと

- Iを個人経験の計数にしない。
- 語形一致をAI使用と読まない。

引継ぎは [phase1-handoff.md](phase1-handoff.md)。状態は[status.json](status.json)。
