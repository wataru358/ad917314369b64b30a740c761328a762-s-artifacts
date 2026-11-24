# D02 Save Common Crawl WARC records and raw HTML

Read the [root rules](../../AGENT.md) and [branch rules](../AGENT.md) before starting this leaf task.

## Goal

For every candidate frozen in D01, retrieve the specified WARC byte range and save the original HTML bytes and acquisition outcome.

## Inputs

- The output_dir of the completed D01 attempt in the same run_id
- D01 candidates and the manifest hash
- Root configuration for the seed, transfer limits, and pilot.cc_records

Resolve upstream files from the upstream output_dir returned by workflow.py and the manifest.

## Steps

1. Verify the frozen D01 artifacts and use the seed to order all candidates. Use the same candidate IDs in filenames.
2. Try the first five records and verify HTTP 206, the received length, and WARC and HTML validation and storage.
3. Retrieve pending candidates one at a time. Request the data, save the WARC, save the HTML, then update the ledger. Resume at the next unfinished chunk.
4. Process retries within their limits and wait deadlines. Finalize outcomes for all candidates, retaining failures. Report success counts and a breakdown of failures, and check the raw data against the ledger.

## Required outputs

Save everything in the output_dir returned by start.
- `report.md`
- `manifest.json`
- `verification.json`
- `summary.json`
- `acquisitions.jsonl`
- `attempts.jsonl`

## Acceptance criteria

- C01 The ledger has exactly one row per D01 candidate in the frozen order. Final rows are marked succeeded or failed with a reason.
- C02 The first five records have documented checks for range retrieval, compression, and saving and reading back the original HTML.
- C03 For each success, the input location, received length, WARC URL, type, internal HTTP 200, and HTML and WARC hashes can be verified. Publication, crawl, and save timestamps are stored in separate fields.
- C04 The ledger retains failure reasons, attempt history, retry limits, and wait deadlines. An independent reviewer checks total counts and hashes of saved files.

Have an independent reviewer verify the saved artifacts and definitions before completion. Check the receipt criteria, artifacts, and hashes, then run workflow.py finish from the root. Completion covers the full task.

## Reference specifications

- [download-spec.md](../download-spec.md#storage-and-resumption)
- [download-spec.md](../download-spec.md#d02-save-warc-and-html-from-specified-byte-ranges)

## Notes

- Record the range response's HTTP 206 and the archived page's HTTP 200 separately.
- WARC-Date records the crawl timestamp. Keep the publication timestamp from the original page and the retrieval timestamp.
- Keep failed outcomes in the original candidate set. Use the designated capture for each candidate.

See [download-handoff.md](download-handoff.md) for the handoff and [status.json](status.json) for status.
