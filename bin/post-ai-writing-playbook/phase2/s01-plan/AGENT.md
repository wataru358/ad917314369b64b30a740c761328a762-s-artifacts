# P2-S01 Lock the comparison and corpus intake plan

Read the [root rules](../../AGENT.md) and [branch rules](../AGENT.md) before starting this task.

## Objective

Confirm the inputs and execution order for comparing the fixed UTC month windows across both acquisition routes.

## Inputs

- R01's verified phase2-inputs.json and the files it indexes
- D03's verified plan.jsonl, responses.jsonl, archived HTML, and raw responses
- Fixed measurement specification and settings

Resolve upstream files using the upstream output_dir and manifest returned by workflow.py. Use paths resolved from the current run instead of absolute paths from earlier conversations.

## Steps

1. Open the output directories from the accepted R01 and D03 receipts. Verify required columns, normalized paths, counts, and ID mappings. Record UTC publication time, retrieval time, CC capture time, and edit time in separate fields.
2. Document differences in cohort scope and definitions from Phase 1. Lock the earlier inclusion decisions and use the common January through October UTC window for 2018–2022 and 2026 as the primary cohort.
3. Record the sequence and access restrictions in plan.json for corpus intake, inclusion decisions, specification lock, D candidate lock, H, independent recomputation, the 18 item decisions, and reporting. Distinguish valid zeros from missing measurements.
4. For the extraction pilot, use the first 50 items in the fixed plan as routine examples. Select up to two items each for code, tables, quotations, nested lists, embeds, cards, short text, warnings, empty bodies, Markdown-only bodies, and parse failures, ordered by SHA256(42:phase2-extraction:<category>:<article ID>). Keep duplicate IDs in a single row with all selection reasons.
5. For the language pilot, keep structural diagnostics separate from the accuracy sample. Use the first 50 items for calibration and the first five items per month in plan order for confirmation, excluding items already selected. Seal the labels before viewing the scores. Retain the original 50/19/50 counts as history.

## Required outputs

Save all outputs under the output_dir returned by start.
- `report.md`
- `manifest.json`
- `verification.json`
- `input-index.json`
- `plan.json`
- `pilot-plan.json`

## Completion criteria

- C01 Check the R01 and D03 receipts, input paths, hashes, required columns, and join keys. List all inputs and exceptions.
- C02 Lock the primary cohort, all 60 year-month cells, weights, D/H, blinding, the order of comparisons, verification and reporting, and the definition version.
- C03 Record extraction and language pilot selection, access order, sample shortfalls, and differences from the full corpus.

Before completion, have a separate reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then apply the receipt with workflow.py finish from the root. Completion requires the full work after the pilot.

## Fixed reference rules

- [measurement-spec.md](../measurement-spec.md)
- [settings.json](../settings.json)
- [comparisons.md](../comparisons.md)

## Interpretation

- The acquisition route and period overlap. Account for differences in coverage between the API and CC.
- The pilot is a small quality check. Full-corpus inclusion decisions and comparisons require verification against every input.

See [phase2-handoff.md](phase2-handoff.md) for the handoff and [status.json](status.json) for status.
