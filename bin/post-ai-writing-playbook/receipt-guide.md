# 完了を記録するreceipt

startが返したoutput_dirに、必要な全成果物とreceipt.jsonを置く。criteriaのIDは末端のstatus.jsonにあるC01からの順序を使う。下記の値・ID・hash・基準数は実際のものに置き換える。架空の担当・終了コード・hashを書かない。

```json
{
  "task_id": "D01",
  "run_id": "実際のrun_id",
  "attempt": "startが返したattempt",
  "scope": "full",
  "verification": {
    "exit_code": 0,
    "reviewer": "実際に独立確認した別担当ID",
    "summary": "保存元表と出力を別実装で照合した。詳細はverification.json"
  },
  "criteria": [
    {"id": "C01", "passed": true, "evidence": ["report.md", "verification.json"]}
  ],
  "artifacts": [
    {"path": "report.md", "sha256": "実際の64桁SHA-256"},
    {"path": "manifest.json", "sha256": "実際の64桁SHA-256"},
    {"path": "verification.json", "sha256": "実際の64桁SHA-256"}
  ]
}
```

ファイルのpathはoutput_dirからの相対パス。親ディレクトリ・別attemptへ出るパスは拒否される。outputsに列挙した全ファイルをartifactsへ入れる。可変数のrawファイルや大きい出力はmanifestへ相対パス・サイズ・hashを記録し、その照合結果をverification.jsonへ残す。全corpusの大きいファイルを毎回hashし直すのではなく、検証済みの保存単位とmanifestで固定する。

CLIが確かめるのは、ID・attempt・full範囲・基準数・根拠の所在・hash・終了コード・別確認者の記録。確認者が実際に作業したか、統計の定義が正しいかは自動保証しない。verifierコード、コマンド、stdout/stderrと終了コード、対象数・欠測・不一致を必ず残す。未支持を0や変化なしで埋めない。

```bash
python3 workflow.py finish D01 --evidence runs/実際のrun_id/download/D01/実際のattempt/receipt.json
```

証拠の改変は次のvalidateでも検出する。親の集約が中断で古くなった場合はsyncで直し、葉の完了を手で捏造しない。
