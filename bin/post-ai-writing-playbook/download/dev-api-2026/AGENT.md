# D03 Retrieve a fixed DEV API sample for January through October 2026

Read the [root rules](../../AGENT.md) and [branch rules](../AGENT.md) before starting this leaf task.

## Goal

Freeze 1,000 candidate IDs per UTC month for a total of 10,000 and save the raw JSON and acquisition outcomes from the public API.

## Inputs

- DEV API listing and detail responses
- UTC interval from 2026-01-01 inclusive to 2026-11-01 exclusive
- Root configuration for the seed, monthly count, and transfer limits

Resolve upstream files from the upstream output_dir returned by workflow.py and the manifest.

## Steps

1. Retrieve one listing page and verify the format and storage of five API detail responses. Use the fixed HTTPS host and keep authorized credentials in memory only.
2. Commit listing pages in page-number order, convert timestamps to UTC, and collect in-window IDs by month. Keep a record of duplicates, discrepancies, and evidence of reaching the lower date bound.
3. Verify that the scan reached the lower bound and that each month has enough candidates. Select 1,000 IDs per month in seeded hash order. Cycle through the months from January to October to assign fixed plan positions.
4. After retrieving and checking the first five planned detail responses, process the rest in chunks. Observe the budget and wait deadlines and reuse saved raw JSON.
5. Reconcile retrieval outcomes for every ID and the monthly counts before eligibility screening. Freeze the ledger and raw JSON hashes and record the verification and handoff.

## Required outputs

Save everything in the output_dir returned by start.
- `report.md`
- `manifest.json`
- `verification.json`
- `summary.json`
- `pages.jsonl`
- `plan.jsonl`
- `responses.jsonl`
- `requests.jsonl`

## Acceptance criteria

- C01 The connection probe records five results. The listing page number and oldest row establish that the scan reached the lower date bound. Saved listing pages are consecutive from page 1, and the report describes the limitations of offset pagination.
- C02 The plan can be reproduced from the seeded hash order and contains 1,000 unique IDs per UTC month from January through October, for 10,000 in total. Selection uses the full eligible set regardless of tags or language attributes.
- C03 The first five planned responses have been saved and read back. Every planned ID has a saved, empty, not_found, or failed outcome. All original planned IDs are accounted for.
- C04 Valid HTTP 200 detail responses are saved, including empty bodies, with verifiable response IDs and hashes. Failures carry reasons. An independent reviewer verifies the monthly breakdown and checks the raw JSON for credentials.

Have an independent reviewer verify the saved artifacts and definitions before completion. Check the receipt criteria, artifacts, and hashes, then run workflow.py finish from the root. Completion covers the full task.

## Reference specifications

- [download-spec.md](../download-spec.md#storage-and-resumption)
- [download-spec.md](../download-spec.md#d03-freeze-1000-records-per-month-in-2026)

## Notes

- Reaching the lower date bound through offset pages leaves overall listing coverage unknown.
- The API body reflects the article at retrieval time. Record HTTP 200, body availability, and English-language eligibility as distinct outcomes.
- Keep the original monthly quotas and IDs even when a month is short or an ID fails.

See [download-handoff.md](download-handoff.md) for the handoff and [status.json](status.json) for status.
