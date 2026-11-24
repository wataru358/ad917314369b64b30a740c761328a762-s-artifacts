# P2-S03 Lock the cohort, measurement specification, and author split

Read the [root rules](../../AGENT.md) and [branch rules](../AGENT.md) before starting this task.

## Objective

Finalize the common months, fixed specification, author split, and confirmation samples for S04 before disclosing results.

## Inputs

- S02's English corpus, records, and manifest
- R01 inclusion decisions, structure, word and sentence implementations, and tags indexed by S01
- Fixed specification and settings

Resolve upstream files using the upstream output_dir and manifest returned by workflow.py. Use paths resolved from the current run instead of absolute paths from earlier conversations.

## Steps

1. Resolve paths from the accepted runs and save settings and input hashes. Select the common UTC months and record exceptions such as unknown dates in the ledger with reasons.
2. Use separate article ID namespaces for the earlier CC and newer API data. Merge only unique known numeric author IDs across routes. Check cohort counts by year and month and missing authors, tags, edited_at, retrieval times, and capture times.
3. Build nonempty exact-match word sequences from fixed S and P/L ordering. Assign D/H by fixed SHA-256 parity of the smallest key in each connected author component. Keep H lexical comparisons sealed.
4. For X02 calibration, select 2 earlier slots per year-month and 10 newer slots per month. For confirmation, select 12 and 30 respectively. Use the fixed salt and one article per author. Separately select 50 calibration and 100 confirmation articles per route, excluding the X02 samples. Isolate the mapping between IDs and blind IDs.
5. Import the fixed word and sentence rules. Use small synthetic fixtures to check apostrophes, Unicode and URLs, fragments, P/L, bold spans, zeros and NA, weights, and insufficient support for intervals.

## Required outputs

Save all outputs under the output_dir returned by start.
- `report.md`
- `manifest.json`
- `verification.json`
- `fixed-cohort.jsonl`
- `metadata-audit.json`
- `settings.resolved.json`
- `author-split.jsonl`
- `samples.jsonl`
- `fixtures.json`

## Completion criteria

- C01 Verify the earlier inclusion decisions, newer English-language IDs, observed counts for all 60 cells, and exclusion reasons against the original inputs.
- C02 Connected components based on authors and nonempty exact text matches stay within one D/H partition. Report unknown authors, component sizes, and support by cell. Pass near-duplicate groups spanning the partitions to S04 diagnostics.
- C03 Keep X02 and automated-definition samples separate. Lock slots, selections, salts, shortfalls, and text hashes by D/H partition.
- C04 Check small examples covering the six metrics' denominators and NA treatment where they differ from Phase 1, lexical boundaries, bold projection, weighting, and bootstrap.

Before completion, have a separate reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then apply the receipt with workflow.py finish from the root. Completion requires the full work after the pilot.

## Fixed reference rules

- [measurement-spec.md](../measurement-spec.md)
- [settings.json](../settings.json)
- [comparisons.md](../comparisons.md)

## Interpretation

- Lock the specification in S03 and keep H results sealed.
- Use separate numeric article ID namespaces for each route. Identify individuals by their numeric author IDs, excluding handles and organization IDs.

See [phase2-handoff.md](phase2-handoff.md) for the handoff and [status.json](status.json) for status.
