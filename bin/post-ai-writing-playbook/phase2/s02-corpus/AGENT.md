# P2-S02 Lock full-text inclusion decisions for the new corpus

Read the [root rules](../../AGENT.md) and [branch rules](../AGENT.md) before starting this task.

## Objective

Record an outcome for every ID in the fixed plan and finalize the accepted English-language 2026 IDs and their extracted prose.

## Inputs

- S01's input-index.json, plan.json, and pilot-plan.json
- Indexed D03 raw responses, HTML, and Markdown
- Indexed T00 extraction rules and T01 language rules

Resolve upstream files using the upstream output_dir and manifest returned by workflow.py. Use paths resolved from the current run instead of absolute paths from earlier conversations.

## Steps

1. Verify raw response IDs, UTC timestamps, and hashes in fixed plan order. Apply the earlier HTML extractor and save P/L/U, prose order, headings, bold spans, DOM mappings, and warnings. Record failures with reasons.
2. Run the fixed pilot. Keep items eligible when they fall into the structural diagnostic for text under 180 characters or have only Markdown. Avoid substituting Markdown without authorization.
3. Apply the earlier automated scoring rules to S, P, L, and 1,200-character sections of S. Review all S content independently of the scores and automated status. Reuse completed pilot rows after confirming identical text hashes. Process the remaining items in batches of up to 25.
4. Read the full text and seal the content labels and evidence. Then open only the corresponding scores. Index batch ranges, timestamps, reviewers, and hashes. Keep the thresholds fixed after review.
5. Hold mixed and uncertain results. Record non-English content, missing prose, and unavailable responses separately. Keep ads, short texts, and technical texts eligible. Append corrections with evidence, timestamp, the score disclosure flag, and the original record hash.
6. Independently check every inclusion decision and structure record and verify the join between the plan and raw responses. Report which inputs were reused and whether corpus intake and decisions were repeated.

## Required outputs

Save all outputs under the output_dir returned by start.
- `report.md`
- `manifest.json`
- `verification.json`
- `records.jsonl`
- `decisions.jsonl`
- `english.jsonl`
- `summary.json`
- `language-review-index.json`

## Completion criteria

- C01 Every plan ID appears once in records and once in decisions, in plan order. Counts by status sum to the total.
- C02 The English corpus matches the ledger's accept_english entries. Retain held items, missing prose, and unavailable responses in the ledger.
- C03 Trace text and evidence to the raw responses. Preserve proof that the corresponding scores were disclosed after the labels were sealed and retain the original decisions in the correction history.
- C04 Distinguish calibration, diagnostics, unused confirmation samples, and full-corpus review. Independently check actual extraction locations, joins, inclusion decisions, and provenance.

Before completion, have a separate reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then apply the receipt with workflow.py finish from the root. Completion requires the full work after the pilot.

## Fixed reference rules

- [measurement-spec.md](../measurement-spec.md)
- [settings.json](../settings.json)
- [comparisons.md](../comparisons.md)

## Interpretation

- The extracted S text and the complete original article have different language assessment scopes.
- The original run's 8,942 acceptances, 220 holds, and 7 corrections are historical comparison figures.

See [phase2-handoff.md](phase2-handoff.md) for the handoff and [status.json](status.json) for status.
