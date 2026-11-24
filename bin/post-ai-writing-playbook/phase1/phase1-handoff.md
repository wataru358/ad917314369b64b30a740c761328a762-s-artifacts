# Resume Phase 1

Run `python3 workflow.py next` for the current run. For a leaf task in progress, reconcile dependency artifacts with the input hashes recorded in the attempt, then resume after the last accepted processing unit. Reuse completed shards when the run, attempt, code, and configuration match. To change an input or measurement rule, record the reason and the change, then continue in a new attempt and preserve the earlier evidence.

## Inputs from D02

Read `acquisitions.jsonl`, `manifest.json`, `summary.json`, `verification.json`, and HTML for successful rows from the completed D02 attempt. Verify each row's ID, path, URL, acquisition state, source for the UTC publication timestamp, CC capture time, and HTML file hash. Retain rows for failed acquisitions. Use counts and article IDs from the current run.

## Outputs for downstream tasks

- T00 passes the input ledger, body extractions for all candidates, extraction code, and extraction states.
- T01 passes `cohort.csv` with inclusion decisions and years, along with language evidence for every candidate.
- T02 passes `articles.jsonl`, `metadata.csv`, `metrics.csv`, `segmentation.py`, `fixtures.json`, and `topic-map.json`.
- T03 passes references to `coverage.csv`, the date ledger, and the cohort summary.
- A04 passes the author connected-component split to A06 and V01. A07 passes the blinded sample and private ID mapping to A11. A06 and A08 pass DOM structure and position ledgers to A11. A09 passes per-metric cells and `weights.csv` to A10, A12, and V01.

After R01 completes, finalize the Japanese materials with the cohort, scales, and reasons for unavailable results, and finalize `phase2-inputs.json`. The index references the D02 HTML acquisition ledger, T00 extractor, T01 inclusion ledger, T02 frozen code and measurement tables, T03 coverage, and A09 weights. Include package-relative paths, SHA-256 hashes, input attempt numbers, and schema versions. Identify the scope, applicable versions, and attempts for the full Phase 1 inputs. Run `python3 workflow.py sync` and `python3 workflow.py validate`.

In the resume record, keep the ID of any unfinished operation, the last saved artifact, dependency hashes, the resume command, and the unverified scope. When measurement confirms zero support or missing inputs, record the reason in the NA row. If losing a dependency prevents resumption, record the files needed for recovery and the reason in status.
