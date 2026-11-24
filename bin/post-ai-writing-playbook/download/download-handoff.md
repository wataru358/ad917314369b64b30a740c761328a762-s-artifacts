# Download handoff

Run `python3 workflow.py next` at the package root to find where to begin. Continue with the same `run_id` and profile and keep in-progress artifacts under their original settings. Use `workflow.py` to update `status.json`.

| Current state | Next action |
| --- | --- |
| D01 index scan is partially complete | Verify `manifest.paths.gz` against the committed file keys. Resume at the first unprocessed key. |
| D02 is unstarted | Verify D01's completion record and `manifest.json` hash. Check WARC and HTML storage on the first five frozen candidates. |
| D02 is in progress | Read the chunk stop reason, `not_before`, and the pending and retryable entries. Verify the cached WARC records and continue with the original candidate set. |
| D03 plan is still open | Read the last committed listing page and evidence for reaching the lower date bound. If page limits or permissions blocked progress, record the reason and conditions for resuming. |
| D03 plan is frozen | Verify the `plan.jsonl` hash against the acquisition ledger. Resume with the next unprocessed or retryable ID. |
| Required artifacts can be read | Have an independent reviewer check the files against the [acquisition specification](download-spec.md). Include the evidence file hashes in the completion receipt and run `workflow.py finish`. |

Pass D02's `acquisitions.jsonl` and `manifest.json` to Phase 1 T00. Failed acquisitions also carry their candidate IDs and failure reasons. Pass D03's `plan.jsonl`, `responses.jsonl`, and `manifest.json` to the Phase 2 corpus task. Make the publication time from the listing, the retrieval time of the detail response, and the body storage outcome accessible.

When handing off interrupted work, record the `run_id`, profile, task, committed artifacts and hashes, next file key or ID, stop reason, and wait deadline. If an external dependency prevents resumption, record the failed action and conditions for recovery. Report acquisition counts and downstream inclusion counts in separate fields.
