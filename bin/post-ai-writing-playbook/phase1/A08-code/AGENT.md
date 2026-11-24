# A08 Code and Nearby Prose

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Measure the amount of code, language labels, and prose before and after code within a heading section.

## Inputs

- T03 cohort
- T00 extracted body_html
- T02 S words, DOM events, and metadata

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Use 12 fixed examples to check pre, highlighted blocks, inline code, unknown language labels, adjacent code, and heading boundaries.
2. Save block and inline code counts and sizes, explicit classes, and statuses for all articles.
3. Match preceding and following prose within the same section, check it against the original S, and flag reused matches.
4. Apply the bundled aggregation and interval thresholds, then independently check the original HTML, denominators, positions, and figure.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `code-events.csv`
- `code-article.csv`
- `code-annual.csv`
- `code-contrasts.csv`
- `code-audit.json`
- `code.svg`

## Completion Criteria

- C01 Code blocks and inline code are counted once, and the original order, adjacent prose matches, and denominators for each status can be reconstructed.
- C02 The 12 fixed diagnostic cases are recorded, with zero, no match, and projection failure distinguishable.
- C03 Aggregates for all 22 metrics, intervals for the 12 specified metrics, and any strata with insufficient support are retained.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a08-code-rules.md](../references/a08-code-rules.md)
- [a08-aggregation.json](../references/a08-aggregation.json)

## Interpretation

- Distinguish the presence of any code from the presence of a code block and keep the visible-character share separate from code characters per S word.
- Preserve unknown language labels as unknown.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
