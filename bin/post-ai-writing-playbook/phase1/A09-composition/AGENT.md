# A09 Changes in Topic and Author Composition

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Measure topic and length composition, weighting across known authors, and within-author differences.

## Inputs

- T02 metrics, metadata, and articles
- T03 coverage
- A01–A08 comparisons and scopes of applicability

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Freeze topic-by-P word-count cells that meet the support threshold of 30 and baseline weights q. Save cell, year, and classification keys for each metric.
2. Compare the full cohort with the common-support cohort, and compare fixed-composition estimates with unadjusted estimates for the same cohort.
3. Give each author equal weight within a year and calculate equally year-weighted within-author differences for authors observed in both periods.
4. Save the contribution decomposition, author-cluster intervals, and the scope of A04–A08. Use the fixed dictionary to label AI topics in tags and AI phrases in body S separately.
5. Recalculate the weights, decomposition, and intervals from the source tables, and independently verify the scopes of applicability.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `metric-support.csv`
- `weights.csv`
- `composition-contrasts.csv`
- `author-year.csv`
- `within-author.csv`
- `decomposition.csv`
- `ai-cues.csv`
- `composition.svg`

## Completion Criteria

- C01 For each metric, the six years of support, common support, fixed weights, effective sample size (ESS), and exclusion rates can be checked.
- C02 Unadjusted and fixed-composition estimates for the same cohort, equal known-author weighting, and within-author point differences and selection rates are distinguishable.
- C03 The decomposition identity, scope of each exploratory analysis, AI labels for tags and body phrases, and rules for unknown states can be verified.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a09-ai-topic.json](../references/a09-ai-topic.json)
- [t02-strata-map.json](../references/t02-strata-map.json)

## Interpretation

- An M01 comparison stratified by each article's own word-count band answers a separate question.
- Limit conclusions to the cohort with sufficient support for the comparison.
- Treat phrase presence as a text feature. AI use and semantic topics require their own evidence.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
