# A06 Headings, Openings, and Endings

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Compare dictionary-based heading functions, concentration of heading patterns, and expressions at article openings and endings.

## Inputs

- T03 cohort
- T02 headings and S/P positions
- A04 split.csv and evidence that candidates were frozen

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Calibrate the fixed heading dictionary on 60 blinded discovery candidates, then freeze the rules and record unmatched headings.
2. Calculate the S cursor and section word count for each heading, along with function sequences, annual concentration, and the size adjustment.
3. Use the first and last 50 P words in the A04 splits. Freeze 15 increasing and 15 decreasing two- to five-word sequences for each window, then validate them in the other split.
4. Independently verify original DOM order, heading hierarchy, concentration by identical text and author, fixed candidates, and the figure.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `headings.csv`
- `heading-sequences.csv`
- `window-candidates.csv`
- `window-holdout.csv`
- `structure-summary.csv`
- `structure.svg`

## Completion Criteria

- C01 The sequence of heading calibration, freezing, and evaluation is recorded, and heading absence, dictionary nonmatches, and concentration can be recalculated.
- C02 The presence of a summary, conditional section length, and S position each have an explicit denominator.
- C03 Opening and ending candidates are frozen before validation. All candidate results and checks for split leakage are verified.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a06-settings.json](../references/a06-settings.json)

## Interpretation

- Assess full-article structural uniformity using evidence beyond the prevalence of summary headings.
- Interpret dictionary labels as rule-based classifications.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
