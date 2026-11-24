# V01 Sensitivity analyses

Read the [root rules](../../AGENT.md) and [Phase 1 rules](../AGENT.md) before starting this task.

## Purpose

Apply the prespecified sensitivity conditions one at a time to determine where the conclusions hold.

## Inputs

- Accepted outputs from A01–A12
- Frozen inputs and features from T00–T03
- A04 duplicate-text components

Resolve upstream files from the upstream output_dir and manifest returned by workflow.py. Use paths from the current run.

## Steps

1. Freeze concrete variant IDs from the bundled condition list. Change one condition at a time.
2. Record comparisons for body regions, sentence boundaries, word forms, language, quality, topics, composition, authors, periods, dates, and duplicates.
3. Count zero support, insufficient support, and missing required inputs. Track implementation failures and pending work with separate states.
4. Independently check differences in scope between historical and current comparisons, A11/A12 exploratory analyses, and counterexamples.
5. Independently verify tables and figures and spot-check source articles for large deviations.

## Required Outputs

Save all outputs in the output_dir returned by the start command.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `variant-plan.json`
- `robustness.csv`
- `exploration-confirmation.json`
- `sensitivity.svg`

## Completion Criteria

- C01 Every planned variant-by-primary-metric cell has a calculated value or a state with a reason. All required work has been processed.
- C02 Independent calculations verify differences from the original comparison, sample sizes, missingness, and support, and distinguish zeros by definition from reversals.
- C03 Unmeasured A04 boundaries and duplication, A11/A12 exploratory results, and figure counterexamples and constraints are saved.

Before completion, have a different person independently verify the saved artifacts and definitions. Check the criteria, artifacts, and hashes in the receipt, then run workflow.py finish from the root. Completion requires the full task to pass after the pilot.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [v01-variants.json](../references/v01-variants.json)

## Pitfalls

- Record unevaluable cases explicitly.
- Assess robustness using more than whether an interval crosses zero.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current state.
