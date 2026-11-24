# A02 Sentence Rhythm and Punctuation

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Compare M02–M04 and the secondary measures while retaining the sentence-count and punctuation denominators.

## Inputs

- T03 cohort and coverage
- T02 P owner blocks, sentences, tokens, and M02–M04

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Count mechanically segmented sentences, sentence lengths and fragments, differences between adjacent sentences, the share of single-sentence paragraphs, and punctuation.
2. Save the equally year-weighted differences in the primary metrics, the author-cluster intervals, and any annual shortfalls.
3. Calculate sentence-based comma intervals, the supplementary result for articles with at least five commas, and the legacy approximation separately.
4. Diagnose low sentence counts, extreme CV values, and candidate untagged code. Check negative cases and aggregates with an independent calculation.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `sentence-annual.csv`
- `rhythm-contrasts.csv`
- `rhythm-diagnostics.json`
- `rhythm.svg`

## Completion Criteria

- C01 M02–M04 are calculated from the fixed P data, with distinct cases for zero words, a single sentence, and low n.
- C02 Sentence-based comma intervals and the legacy article-level approximation are in separate columns. Commas within numbers are excluded.
- C03 The author-cluster intervals and figure can be independently verified from the inputs.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a02-settings.json](../references/a02-settings.json)

## Interpretation

- Report sentence-length CV as NA for a single sentence.
- Treat burstiness as a transformation of CV.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
