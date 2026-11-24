# 最初にAIへ渡すプロンプト

```text
このフォルダーのAGENT.mdを読み、DEV英語記事のpost-ai-writing調査を新しいrunで開始してください。
計画を述べるだけで終わらず、実行できる作業を始めてください。

1. まず作業場所がこのplaybookルートか確認する。外側のリポジトリにいる場合はbin/post-ai-writing-playbookへ移動する。python3 --versionを確認し、3.11以上の実行ファイルを選ぶ。以降のpython3はその実行ファイルを使う。python3 selftest.pyとpython3 workflow.py validateを実行する。selftestは一時フォルダーの架空データだけを使い、研究は実行しない。validateのerrorがstaleで始まる場合だけsyncしてvalidateを再実行する。initialization incompleteなら、既存run_idと同じIDでinitしてvalidateを再実行する。それ以外の整合性エラーは隠さず、原因と保存物を確認する。
2. config.jsonのrun_idがnullなら、現在の日時を含む新しいIDを決め、python3 workflow.py init --run-id <ID>で固定する。既存IDがあれば変更しない。同じIDでinitを再実行しても既存の確定状態は初期化されない。
3. python3 workflow.py nextを読み、in_progressがあれば引継ぎとcheckpointから再開する。以前の担当が動いていればその担当に任せる。停止を確認した後だけblock/retryで新attemptへ移す。理由を記録する。
4. readyから依存関係を満たす末端を一つ選ぶ。枝と末端のAGENT.md・引継ぎを読み、python3 workflow.py start <ID> --owner <担当ID>で所有する。返されたoutput_dirにコードと成果物を置く。
5. 指示の規則を実装し、少数のpilotで確認後、固定した全量をチャンクごとに処理する。処理上限に達したらcheckpointから同じattemptを続ける。実装や必要な入力がない場合は作るか、解けない阻害だけ理由付きでblockにする。
6. 別担当が独立確認し、acceptance_criteriaごとの根拠、必要な全出力、SHA-256、実際の検証結果をreceipt.jsonへ記録する。CLIが受理しただけで内容の正しさが証明されたとは扱わない。
7. python3 workflow.py finish <ID> --evidence <ルートからのreceipt相対パス>で完了を反映する。親の進捗は自動集約される。
8. python3 workflow.py nextへ戻り、可能な作業を続ける。全部完了するか、進められる仕事がなく阻害が残るまで進める。別担当への分担は利用できる枠内で行い、同じファイルへ同時に書かない。
9. 中断するときは引継ぎを更新し、python3 workflow.py syncとvalidateを実行する。完了・未完了・阻害・次の一操作と、今回の結果で言える範囲を短く報告する。

原データ・既存runは変更しない。過去と同じ数値を出すことを合格条件にしない。
Phase 1とPhase 2の期間、指標、分母、正式判断を混ぜない。
新しい収録が元の保存物と違う場合は、新しい方法再現として差を記録する。
```

再開時も同じプロンプトを渡せます。モデルが手元のファイル・コマンド・必要なネットワークを操作できる環境で使ってください。この文書自体が定期ジョブを登録したり、AIを常駐起動したりするものではありません。
