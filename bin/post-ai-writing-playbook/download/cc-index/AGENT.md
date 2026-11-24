# D01 Freeze the Common Crawl DEV candidates

Read the [root rules](../../AGENT.md) and [branch rules](../AGENT.md) before starting this leaf task.

## Goal

Use the public CC-MAIN-2025-43 Parquet index to freeze the dev.to candidate paths that meet the definition and select a capture location for each path.

## Inputs

- Root configuration for the crawl, seed, transfer limits, and pilot.cc_records
- The cc-index-table.paths.gz file and subset=warc Parquet index for the selected crawl

Resolve upstream files from the upstream output_dir returned by workflow.py and the manifest.

## Steps

1. Freeze the list source, compression limit, filters, and candidate route definition. Verify the saved list hash before reusing it.
2. Read only the required columns and ranges in key order. Read back five candidates from the index first to verify deduplication and capture selection.
3. Commit the file counts and candidates together. Continue within the configured limits until all keys in the saved list have been processed.
4. Write the candidate list with the earliest capture frozen for each path. Have an independent reviewer verify file completion, candidate IDs and paths, and counts from the saved artifacts.

## Required outputs

Save everything in the output_dir returned by start.
- `report.md`
- `manifest.json`
- `verification.json`
- `summary.json`
- `manifest.paths.gz`
- `index-files.jsonl`
- `candidates.jsonl`

## Acceptance criteria

- C01 The saved compressed list matches the SHA-256 in the manifest, and its eligible keys correspond one-to-one with the processed index ledger.
- C02 The five-candidate pilot records the index filters, normalized paths, and capture locations.
- C03 Candidate rows are unique and sorted by path. Recomputed IDs match every row, and capture locations follow the timestamp and tie-breaking rules.
- C04 Per-file counts agree with the totals. The report confirms processing of every index file and distinguishes the covered scope from historical reference counts.

Have an independent reviewer verify the saved artifacts and definitions before completion. Check the receipt criteria, artifacts, and hashes, then run workflow.py finish from the root. Completion covers the full task.

## Reference specifications

- [download-spec.md](../download-spec.md#storage-and-resumption)
- [download-spec.md](../download-spec.md#d01-freeze-candidates-and-capture-locations)

## Notes

- HTTP 200 and HTML are index acquisition filters. Assess the article body, publication year, and English-language eligibility later.
- Report partial index counts as partial. Leave counts for unprocessed keys missing.

See [download-handoff.md](download-handoff.md) for the handoff and [status.json](status.json) for status.
