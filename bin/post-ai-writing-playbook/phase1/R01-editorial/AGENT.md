# R01 Japanese editorial materials

Read the [root rules](../../AGENT.md) and [Phase 1 rules](../AGENT.md) before starting this task.

## Purpose

Compile the comparisons and exploratory analyses into verified Japanese editorial materials and pass frozen inputs to Phase 2.

## Inputs

- T03 cohort and coverage
- Source tables, figures, manifests, and verification from A01–A12 and V01
- Input assets from T00/T01/T02/A09

Resolve upstream files from the upstream output_dir and manifest returned by workflow.py. Use paths from the current run.

## Steps

1. Describe the cohort, primary comparisons, concrete material, positions, structure and style, counterexamples, and limitations in Japanese.
2. Verify the two metrics without a specified direction, the pre-result freeze time, the separate population for author-based intervals, and whether the p-value and Holm procedures ran.
3. Save the claim ledger and source table index, reasons for withholding claims, and limitations for each comparison cohort.
4. Open the figures and check that the values, sample sizes, periods, and intervals match the descriptions.
5. Register D02, the T00 extractor, T01 inclusion decisions and detector, T02 segmentation, metadata, and topic map, T03 coverage, and the A09 fixed q in phase2-inputs.json.
6. Have an independent reviewer check facts, measurements, figures, hashes, and relative references.

## Required Outputs

Save all outputs in the output_dir returned by the start command.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `primary-metrics.csv`
- `claims.csv`
- `figure-captions-ja.csv`
- `source-result-index.csv`
- `phase2-inputs.json`

## Completion Criteria

- C01 The scales of the six primary metrics, source tables, point estimates for articles and known authors, interval populations, comparison years, and labels for tests left unrun all agree.
- C02 Claims and withheld conclusions can be traced to source table rows, denominators, counterexamples, and shortfalls. The existing figures were opened and checked.
- C03 Every required Phase 2 input resolves by package-relative path and hash, and all required issues have been resolved.

Before completion, have a different person independently verify the saved artifacts and definitions. Check the criteria, artifacts, and hashes in the receipt, then run workflow.py finish from the root. Completion requires the full task to pass after the pilot.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)

## Pitfalls

- Base acceptance and withholding on this run's evidence. The original run recorded 22 accepted and four withheld claims.
- Treat drafting the Japanese article, translating it into English, and publishing it as separate tasks.
- Connect results across different cohorts only where the evidence supports the relationship.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current state.
