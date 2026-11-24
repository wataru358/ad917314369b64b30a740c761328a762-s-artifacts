# P2-S05 Verify the arithmetic and scope of claims for 18 items

Read the [root rules](../../AGENT.md) and [branch rules](../AGENT.md) before starting this task.

## Objective

Determine what the measurements and comparisons support using the saved values. Make decisions and evidence traceable.

## Inputs

- S04 comparisons, article values, assessments, denominators, diagnostics, and independent readback
- S03 cohort, settings, samples, and input hashes

Resolve upstream files using the upstream output_dir and manifest returned by workflow.py. Use paths resolved from the current run instead of absolute paths from earlier conversations.

## Steps

1. Check the cohort manifest and all comparison keys. Distinguish reused S04 recalculations from checks performed at this stage. Extract denominators, monthly support, valid replicates, corrections, and NA reasons from the saved comparisons.
2. Join all fixed sensitivity rows and distinguish direction, changes in population, insufficient support, and inapplicability. Keep the quality sample's baseline, display-error, advertising, and signature comparisons across all six M metrics, with reasons.
3. Check for consensus references, manual segmentation count differences, bold provenance, and positive and negative support for V03, X01, and X03. For each of E and G in the fixed X02 sample, check presence, word rate, assessable counts, agreement and κ, and the uncertainty range due to unknown labels.
4. Check F/R/A, raw author counts, Q, and unmet replication conditions for V. For C01, check the four-point extrapolation on the original scale, out-of-domain values, backtests, and sensitivities. Identify remaining differences in acquisition, survival, editing, and topic composition.
5. Use evidence to assign each of the 18 items limited acceptance, hold, or indeterminate. Distinguish observed automated values from measurement validity. Record permissible wording and evidence locations for every item. Have a separate reviewer verify the evidence and wording.

## Required outputs

Save all outputs under the output_dir returned by start.
- `report.md`
- `manifest.json`
- `verification.json`
- `item-decisions.json`
- `robustness.tsv`
- `evidence-index.json`
- `independent-review.json`

## Completion criteria

- C01 Retain exactly 18 decisions covering the six M metrics, V01/V02, five V03 series, X01, X02 E/G, X03, and C01. Link them to all comparison keys and fixed sensitivities.
- C02 Provide values, denominators, uncertainty, content verification, alternative explanations, and permissible wording for each decision. Give reasons for NA and unknown values.
- C03 Retain X02 fixed-sample differences and bounds due to unknown labels, unmet V02 criteria, all 24 quality comparisons, and the six C01 metrics and backtests.
- C04 Have an independent reviewer check the saved values against the wording. Save findings, corrections, and verification of corrections. Completion requires checking every item and saving its decision.

Before completion, have a separate reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then apply the receipt with workflow.py finish from the root. Completion requires the full work after the pilot.

## Fixed reference rules

- [comparisons.md](../comparisons.md)
- [phase2-handoff.md](../phase2-handoff.md)
- [measurement-spec.md](../measurement-spec.md)

## Interpretation

- The original run's 2 limited acceptances, 14 holds, and 2 indeterminate decisions are historical. Assign the new run's decisions from its own evidence.
- Rerun the full calculation and bootstrap only to investigate a specific discrepancy that the existing checks cannot resolve.

See [phase2-handoff.md](phase2-handoff.md) for the handoff and [status.json](status.json) for status.
