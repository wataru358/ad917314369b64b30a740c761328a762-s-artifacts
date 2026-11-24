# A10 Timing of Changes

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

After checking support, report the fixed boundary, placebo boundaries, exploratory breakpoints, and limits of extrapolation.

## Inputs

- T03 coverage/date-ledger
- T02 six main metrics and author IDs
- A09 weights.csv, support, and cohort

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Build annual, monthly, quarterly, and supplementary January–September grids and cohorts. Freeze support diagnostics before examining values.
2. Fit the prespecified regression with seasonality and actual calendar time t in supported windows. Verify the treatment of November and December 2022 and the calendar-lag HAC calculation.
3. Check pre-trends and the 2020 and 2021 placebo boundaries. Compare composition within the same months and retain rows with insufficient support.
4. Compare models with zero or one breakpoint across all candidate BIC scores, resample contiguous blocks, and apply the stability criteria.
5. Use synthetic data with missing observations and a complete example to independently verify coefficients, HAC, candidate masks, some or all replicates, and figures.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `time-grid.csv`
- `support.csv`
- `time-models.csv`
- `break-candidates.csv`
- `block-replicates.csv`
- `time-stability.csv`
- `time.svg`

## Completion Criteria

- C01 The grid for the full period, supported windows, reasons for insufficient support, seasonality, and the cohort and fixed-q masks can be reproduced.
- C02 Records cover the fixed boundary, pre-trend checks, both placebo boundaries, candidate BIC scores, and block-resampling statuses and failed replicate IDs.
- C03 Calendar-lag HAC, numerical results, plotted points, and stopping conditions are checked by independent calculation.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a10-methods.json](../references/a10-methods.json)

## Interpretation

- Treat a support table equivalent to S02 as a diagnostic. Estimation is a separate step.
- Use calendar time so missing months remain visible in the time index.
- Report supported timing for each metric individually. Counterfactual estimates and claims that AI caused the changes require a separate design.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
