# A11 Position of the First Concrete Material

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Measure mechanically detected positions across all articles and locate the first title-relevant material in the fixed evaluation sample.

## Inputs

- T02 mapping between S words and the DOM
- A06 headings.csv
- A07 fixed evaluation and calibration samples
- A08 code-events.csv

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Freeze the candidate dictionary and the title-relevance rubric using the calibration sample. Link A06/A08 DOM positions to S words and save the first mechanically detected occurrence for all articles.
2. Read A07 evaluation articles in full with the year hidden, and record the first material that addresses the title and the S and DOM spans that support it.
3. Reevaluate 32 prespecified articles in an independent top-level session, withholding the initial ratings, and adjudicate disagreements.
4. For each year pair in the fixed strata, require support of 30 for presence and 20 for position. Retain unsupported content comparisons.
5. Independently reread source text, recalculate positions, test negative cases for incorrect positions and S=0, and verify plotted values.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `structure-position.csv`
- `position-rubric.json`
- `coded-position.jsonl`
- `rereview.json`
- `position-comparisons.csv`
- `position-correspondence.csv`
- `position.svg`

## Completion Criteria

- C01 S cursor alignment agrees across all adopted articles. Positions are available for the four automated candidates, and zero, absence, missing input, and an undefined proportion are distinguishable.
- C02 Every article in the fixed A07 sample has a recorded title promise, an evidence span, and an out-of-S anchor or reason an assessment could not be made, as applicable. Separate-session reevaluation and adjudication are retained.
- C03 The correspondence between automated and content measures, sample sizes and support by stratum, counterexamples, and checks against the plotted values are recorded.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a11-candidate-dictionary.json](../references/a11-candidate-dictionary.json)
- [a11-rubric.md](../references/a11-rubric.md)

## Interpretation

- The historical run used 38,980 articles for automated measures and 128 for content review. Attribute findings to the applicable cohort.
- Interpret earlier positions as positional measures. Reading time and quality require their own evidence.
- Use a separate top-level session for reevaluation, with a different worker in the same conversation treated as part of the original session.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
