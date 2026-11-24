# A03 Lists, Bold Text, and Headings

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Compare how often articles use structural elements, how extensively they use them, and where they appear in S.

## Inputs

- T03 cohort and coverage
- T02 articles, DOM events, bold text, and M05/M06

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Calculate primary M05/M06, the presence and amount of structural elements, and heading density and candidates.
2. Save counts for each half and each 20/60/20 region using the original S word ranks.
3. Select quality-check candidates by the fixed rule and compare them with the raw and cleaned DOM.
4. Independently reconstruct positions, denominators, primary contrasts, intervals, and the figure.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `format-annual.csv`
- `format-contrasts.csv`
- `format-positions.csv`
- `format-audit.json`
- `formatting.svg`

## Completion Criteria

- C01 The equally year-weighted estimates and intervals for M05/M06, structural presence, and conditional intensity can be recalculated.
- C02 Counts of S words, L words, bold words, and bold spans agree for each region.
- C03 Empty regions, S=0, absent structures, projection failures, and the role of illustrative examples are distinguishable.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a03-settings.json](../references/a03-settings.json)

## Interpretation

- Record zero when there is no list and the S word count is positive. Record NA when there are no S words.
- Track bold spans and bold words separately, and distinguish DOM lists from the presence of L words.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
