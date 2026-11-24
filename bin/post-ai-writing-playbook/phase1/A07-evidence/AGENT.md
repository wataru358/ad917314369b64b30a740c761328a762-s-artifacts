# A07 Personal Experience and Concrete Verification Details

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Read content descriptions in a fixed blinded sample and examine how they correspond to automated proxies across all articles.

## Inputs

- T03 cohort
- T02 original DOM, sentence units, source article text, and metadata
- A05 voice-article.csv

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Order each year's articles by a fixed hash and save four for calibration and sixteen for evaluation. Hide year and author, then freeze the content rubric and proxy dictionary separately.
2. Select four evaluation articles per year and save a fixed packet for a separate session. Read every evaluation article in full and record evidence, S sentence IDs, status, content type, and operation mode for five categories.
3. Retain the unopened inputs, execution record, and adjudication for the separate-session reevaluation.
4. Measure all 25 proxies corpus-wide using fixed P phrase, number, link, and DOM rules. Check how A05 word forms correspond to content within the same sample.
5. Summarize upper and lower bounds, each denominator, article types, years, word-count bands, and proxy disagreements. Have another reader audit the evidence and check the counts with an independent implementation.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `sample-manifest.json`
- `rubric.json`
- `coding-ledger.jsonl`
- `rereview.json`
- `proxy.csv`
- `correspondence.csv`
- `evidence-summary.csv`

## Completion Criteria

- C01 The fixed calibration and evaluation samples are disjoint. Every evaluation article is read in full after the rules are frozen, and each article has an evidence-backed status and span.
- C02 The fixed subset is reevaluated in a separate session. The initial review, reevaluation, and adjudication are retained.
- C03 Corpus-wide proxies, sampled content, S and P denominators, indeterminate cases, and insufficient support are distinguishable.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a07-sample-settings.json](../references/a07-sample-settings.json)
- [a07-content-rules-v1.json](../references/a07-content-rules-v1.json)
- [a07-proxy-settings-v1.json](../references/a07-proxy-settings-v1.json)

## Interpretation

- Distinguish whether the author did the work, whether the article reports it, and whether the proxy matches.
- Keep indeterminate cases distinct from confirmed absence.
- Record any missing reevaluation or unavailable detailed coding explicitly.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
