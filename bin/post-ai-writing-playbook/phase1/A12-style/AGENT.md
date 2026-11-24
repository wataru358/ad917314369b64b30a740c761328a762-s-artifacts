# A12 Style Distances and Distributional Shifts

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Measure changes in the distributions of six metrics and distances from a fixed baseline for formatting and author voice.

## Inputs

- T02 primary metrics, heading density, and P sentences
- A05 grammatical person and contractions
- A09 topic, P word-count band, and cohort tables
- T03 coverage

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Calculate annual quantiles, zero-use shares, and the shares below, above, and exactly at baseline thresholds for the six metrics.
2. Compute fixed midranks from the baseline empirical CDF for complete cases. Account for each metric group, constant values, and missing values.
3. Measure common support for each group and stratum, then sample different-author pairs uniformly and summarize their distances.
4. Check a secondary sampling scheme that selects author pairs first, and diagnose exact matches among saved sentences shared between articles.
5. Use an independent implementation to check the baseline CDF, weights, selected pairs, denominators, and figure.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `quantile-shifts.csv`
- `fixed-reference.json`
- `pair-ids.csv`
- `style-distance.csv`
- `sentence-sharing.csv`
- `style.svg`

## Completion Criteria

- C01 The equally year-weighted baseline CDF, quantiles, and ties can be reproduced.
- C02 Complete cases, common strata, fixed weights, and seeded different-author pair IDs and distances can be verified for each group.
- C03 Original scales, endpoint values, unknown categories, cohort coverage, equal author weighting, exact-text diagnostics, and pair dependence are documented.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a12-distance.json](../references/a12-distance.json)

## Interpretation

- Account for dependence between pairs that share an article or author.
- Report the two style distances individually as measures of formatting and voice.
- Limit results for the unknown stratum to articles in that stratum.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
