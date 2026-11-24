# P2-S04 Run the calculations and independent assessments against the fixed specification

Read the [root rules](../../AGENT.md) and [branch rules](../AGENT.md) before starting this task.

## Objective

Calculate the six core metrics, vocabulary, X01–X03, and C01 on the fixed cohort. Save support, uncertainty, and verification evidence.

## Inputs

- Cohort, settings, D/H assignments, samples, and tests sealed by S03
- Original inputs and fixed extraction, word, and sentence implementations referenced by the S03 manifest

Resolve upstream files using the upstream output_dir and manifest returned by workflow.py. Use paths resolved from the current run instead of absolute paths from earlier conversations.

## Steps

1. Verify the S03 hashes and synthetic fixtures. Apply the earlier word, sentence, and bold projection rules to the new data and reuse the canonical intermediate values for the earlier data. Keep denominators for P sentences and P+L distinct. Record each article's M01–M06 values, numerators, denominators, reasons, and positions.
2. Use only D to apply V01's same-period rules of 20 occurrences, 10 authors, a maximum author share of 0.20, and fixed ranking. Apply V02's rules of earlier R≤1%, newer R≥2%, 20 newer authors, share≤0.10, and newer F≥0.05/1000. Cap V01 at 200 and V02 at 100. Apply the fixed V03 queries to all five series. Seal the classifications, X01 dictionary, and validation sample before checking all candidates on H.
3. Classify candidate X01 5-grams on D. The primary dictionary includes general explanation entries with no exclusion flags. Within each H period, divide the union of matching word positions for phrases used by at least two other authors by W_B. For X03, test the fixed 5 opening and 8 closing expressions in the first and last 50 words respectively, with the close as primary. Keep headings, overlaps in short articles, and shared signatures as supplementary outputs.
4. Use the S03 blind IDs to assign X02 and the separate automated-definition sample to two independent AI assessment streams. Save reviewer, packet, evidence, and original response, and seal both streams before either sees the other. Label E and G separately for each sentence. Record disagreements, indeterminate cases, word-rate bounds, agreement and κ, and required cells. Mark checks without a reference as unverified.
5. Produce F/R/A, D/H counts, NA, separate exploration for unknown authors, and complete yearly and monthly tables. Distinguish primary values, sensitivity estimates, near-duplicate groups, topic support and excluded mass, 200-word windows, and tag exclusions. Keep separate V01 and V02 rows for shared terms and apply BH once to the union of hypotheses.
6. Resample author clusters with PCG64 and the fixed seed. Record the monthly and earlier-year weights, per-replicate C01 regression and pooled SD, extrapolation backtests, and the family covered by each correction. Save the comparison index, independent arithmetic and interval readback, and rerun commands.

## Required outputs

Save all outputs under the output_dir returned by start.
- `report.md`
- `manifest.json`
- `verification.json`
- `article-measures.jsonl`
- `lexical-candidates.json`
- `comparisons-summary.jsonl`
- `yearly-monthly-index.json`
- `annotations-index.json`
- `diagnostics.json`
- `readback.json`

## Completion criteria

- C01 Trace original data, settings, code, environment, D/H, samples, and dictionaries by hash. Seal D selections and classifications before opening H.
- C02 Map the six M metrics to every article. Output calculations, support, intervals, and failure reasons for all V01/V02 candidates, the five fixed V03 series, X01–X03, and C01.
- C03 Retain two independent AI assessments for X02 and the automated-definition verification records. Positive spans, manual counts, missing values, and unknowns are verifiable. Identify slots with insufficient sample support.
- C04 Independently reproduce the handling of 5,000 replicates, the 4,750 valid-replicate requirement, Holm/BH, zero denominators, required months, and each fixed sensitivity. List all comparison keys and check coverage and original values.

Before completion, have a separate reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then apply the receipt with workflow.py finish from the root. Completion requires the full work after the pilot.

## Fixed reference rules

- [measurement-spec.md](../measurement-spec.md)
- [settings.json](../settings.json)
- [comparisons.md](../comparisons.md)

## Interpretation

- Keep years, months, candidates, samples, and thresholds fixed even when results are weak.
- Record failures to meet accuracy thresholds and processing failures separately. Use separate evidence for computational checks and content validity.
- C01 is a descriptive extrapolation of four earlier annual means. The author bootstrap quantifies variation across author clusters, leaving changes in year-level structure outside its scope.

See [phase2-handoff.md](phase2-handoff.md) for the handoff and [status.json](status.json) for status.
