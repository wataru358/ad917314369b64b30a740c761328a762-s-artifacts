# A01 Article and Paragraph Length

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Compare P and S word counts and paragraph lengths, and produce the primary M01 comparison.

## Inputs

- T03 coverage and cohort
- T02 articles, metadata, and M01
- T00 extraction results and original HTML for the fixed sample

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Compute annual P and S word count distributions and bands, the January–September supplementary results, and the M01 point estimates for all articles and for known authors, along with the author-cluster interval.
2. Calculate the median length of P paragraph owners and construct distributions that weight paragraphs equally and articles equally.
3. Audit the prespecified longest-article candidates for each year against the original HTML.
4. Use separate formulas to check the year weights, log scale, interval replicates, and figure.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `annual-length.csv`
- `paragraph-distributions.csv`
- `length-audit.json`
- `m01-contrast.csv`
- `length.svg`

## Completion Criteria

- C01 The equally year-weighted M01 difference on the log1p scale, raw word counts, all-article point estimate, and author-cluster interval can be reproduced.
- C02 The article-weighted and paragraph-weighted paragraph distributions are reported separately.
- C03 The selection rule and audit results for long articles are recorded, and zero words and NA are distinguishable.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a01-settings.json](../references/a01-settings.json)

## Interpretation

- Interpret raw word counts and differences on the log scale as distinct quantities for M01.
- Use paragraph data to draw conclusions about paragraph length.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
