# Record completion with a receipt

Place all required artifacts and `receipt.json` in the `output_dir` returned by `start`. Use the criterion IDs in the leaf's `status.json`, starting at C01. Replace the example values, IDs, hashes, and criterion count with the actual ones. Record the reviewer, exit codes, and hashes from the work performed.

```json
{
  "task_id": "D01",
  "run_id": "actual run ID",
  "attempt": "attempt returned by start",
  "scope": "full",
  "verification": {
    "exit_code": 0,
    "reviewer": "ID of the independent reviewer who performed the check",
    "summary": "Checked the saved source table against the output using a separate implementation. See verification.json for details."
  },
  "criteria": [
    {"id": "C01", "passed": true, "evidence": ["report.md", "verification.json"]}
  ],
  "artifacts": [
    {"path": "report.md", "sha256": "actual 64-character SHA-256 hash"},
    {"path": "manifest.json", "sha256": "actual 64-character SHA-256 hash"},
    {"path": "verification.json", "sha256": "actual 64-character SHA-256 hash"}
  ]
}
```

Each `path` is relative to `output_dir`. Paths that reach a parent directory or another attempt are rejected. Include every file listed in `outputs` under `artifacts`. For a variable number of raw files or large outputs, record relative paths, sizes, and hashes in the manifest and save the verification results in `verification.json`. Freeze the corpus using verified storage units and the manifest to avoid rehashing every large file each time.

The CLI checks IDs, attempt identity, full scope, criterion count, evidence locations, hashes, exit status, and the independent reviewer record. Establish that the reviewer performed the checks and that the statistical definitions are valid through the review itself. Keep the verifier code, commands, stdout and stderr, exit status, counts, missing values, and mismatches. Preserve unsupported results as such.

```bash
python3 workflow.py finish D01 --evidence runs/ACTUAL_RUN_ID/download/D01/ACTUAL_ATTEMPT/receipt.json
```

The next `validate` also detects changes to evidence. If an interruption leaves parent status stale, repair it with `sync` and derive leaf completion from the receipts.
