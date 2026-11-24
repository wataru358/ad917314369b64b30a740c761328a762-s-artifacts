# T03 Cohort statistics and coverage

Read the [root rules](../../AGENT.md) and [Phase 1 rules](../AGENT.md) before starting this task.

## Purpose

Produce tables and figures that show candidate counts, valid coverage, missing data, and distributions.

## Inputs

- T00 input and extraction ledgers
- T01 cohort.csv
- T02 articles, metrics, and metadata

Resolve upstream files from the upstream output_dir and manifest returned by workflow.py. Use paths from the current run.

## Steps

1. Join dates, acquisition state, language state, and inclusion decisions for every candidate. Check for missing and duplicate rows.
2. For included articles, aggregate P/L/U/S totals, medians, quantiles, and word-count bands including zero. Summarize date availability and denominators for identical text, authors, tags, and organizations.
3. Build complete grids for UTC months and quarters. Use settings and acquisition evidence to classify them as complete, partial, unobserved, or unknown.
4. Open the figure files and independently check points, yearly denominators, and NA values against the source tables.

## Required Outputs

Save all outputs in the output_dir returned by the start command.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `coverage.csv`
- `scope.csv`
- `date-ledger.csv`
- `word-bands.csv`
- `overview.svg`

## Completion Criteria

- C01 Article counts reconcile from candidacy to inclusion. P/L/U/S word counts, bands, and quantiles can be recalculated.
- C02 Coverage states for eight years, 96 months, and 32 quarters identify partial years explicitly.
- C03 Year and period counts distinguish unknown dates, known authors, organizations, tags, and duplicate text.

Before completion, have a different person independently verify the saved artifacts and definitions. Check the criteria, artifacts, and hashes in the receipt, then run workflow.py finish from the root. Completion requires the full task to pass after the pilot.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [t03-settings.json](../references/t03-settings.json)

## Pitfalls

- Keep unobserved months in 2025 distinct from months with zero articles.
- Describe counts as counts for the archived cohort.
- Derive publication years from publication dates.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current state.
