# post-ai-writingを新しいrunで再現する

[START.md](START.md)のプロンプトを、ファイルとコマンドを操作できるAIへ渡す。取得、最初の比較、2026年との比較を三層の指示で進め、status.jsonで状態を追う。

```text
AGENT.md / AGENTS.md / START.md / status.json
├── download/AGENT.md / download-handoff.md / status.json
│   ├── cc-index/AGENT.md / download-handoff.md / status.json
│   ├── cc-html/AGENT.md / download-handoff.md / status.json
│   └── dev-api-2026/AGENT.md / download-handoff.md / status.json
├── phase1/AGENT.md / phase1-handoff.md / status.json
│   └── T00〜T03、A01〜A12、V01、R01の18末端
└── phase2/AGENT.md / phase2-handoff.md / status.json
    └── P2-S01〜P2-S06の6末端
```

作業ノードはルート・枝・末端の3層。仕様・参照実装・run成果物は別に置く。各層のAGENT.mdが実行規則、引継ぎが再開先、status.jsonがRalph風のuser_storiesとacceptance_criteria、passesを持つ。親の状態は末端から自動集約する。合計27末端はすべて未着手で配布し、過去の完了状態はコピーしない。

## 先に動かして確かめる

Python 3.11以上、macOSまたはLinuxで実行する。最初に `python3 --version` を確認し、古ければ `python3.11` など利用可能な3.11以上の実行ファイルを選ぶ。以後のpython3は選んだものを使う。進捗管理と例は標準ライブラリだけを使う。実分析に必要なライブラリは、担当が専用環境へ用意して版を固定する。

```bash
python3 selftest.py
python3 example_measure.py
python3 workflow.py validate
python3 workflow.py next
```

selftestは別の一時フォルダーで、依存関係、所有権、中断再開、証拠なし完了の拒否、改変検出、親集約、移動後の再読取りを試す。実データを取得せず、この調査のstatusは変えない。example_measure.pyは架空2記事で、Phaseごとの分母と0・NAの違いを示す小さな計算例。完全な本文抽出器ではない。

## 状態の扱い

`not_started → in_progress → complete`。進められない理由があれば`blocked`とし、解消後に`retry`する。所有者が同じstartは同じattemptの再開となる。異なる所有者は二重起動できない。古い担当の停止を確認せずretryしない。完了タスクの再計算や初期化は別run・別コピーで行う。

```bash
python3 workflow.py init --run-id 20261124-dev-writing-v1
python3 workflow.py start D01 --owner controller-1
python3 workflow.py status
python3 workflow.py block D01 --reason '接続上限に達し、再開時刻を記録した'
python3 workflow.py retry D01 --reason '前担当の停止と上限解除を確認した'
python3 workflow.py sync
```

init時にconfig.jsonとschedule.jsonをrun-lock.jsonで固定する。実行途中に設定・基準を変更せず、別runで扱う。初期化が中断した場合は同じrun_idでinitを再実行する。

チャンクの時間・通信量・リクエスト上限はconfig.json。5件程度のprobeで確認してから全量へ進める。全量未処理のタスクをpilotだけでcompleteにしない。通信量を測れないクライアントで、上限を守れたと報告しない。

`finish`は末端のoutput_dirにあるreceipt.jsonを読む。schemaと例は[receipt-guide.md](receipt-guide.md)。全出力とハッシュ、全基準の根拠、独立確認者、検証成功を要求する。統計の妥当性まではCLIに自動判定できないので、独立確認の中身を保存する。処理の完了は、増加やAIの影響が証明されたという意味ではない。

## 同じ手順と同じ数値

標準は方法の再現。旧比較は2018〜2021年対2023〜2024年、Phase 2は2018〜2022年対2026年のUTC1〜10月。定義・重み・著者分割・欠測・確認方法を保ち、新しく得た結果を記録する。

過去の数値を完全一致で再現するには、同じスナップショット、旧記事ID対応、入力順、コード・依存版、AI判定の実モデルと保存判定まで必要。新しいパスhash IDで同じseedを使っても、旧SQLite IDで選んだ標本とは一致しない場合がある。記事の編集・削除やAPIの列挙範囲も変わる。元の個人環境の絶対パスは実行に不要。

このパッケージの作成では実研究を起動していない。公開やpush/deployも含まれない。raw記事は新runに保存し、配布物へ混ぜない。

作成時の確認は[verification.json](verification.json)と[42件の実動作試験](verification-selftest.json)。これはプレイブックと進捗管理の確認であり、実研究の完了記録ではない。
