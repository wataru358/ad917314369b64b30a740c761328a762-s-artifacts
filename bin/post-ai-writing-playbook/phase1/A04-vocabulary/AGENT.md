# A04 Vocabulary Discovery and Validation

Read the [root rules](../../AGENT.md) and the [branch rules](../AGENT.md) before starting this task.

## Purpose

Validate changes in the fixed candidate phrases across periods, keeping authors and exact P duplicates on one side of the split.

## Inputs

- T03 cohort
- T02 original P sentences, owner units, tokens, L/H, MATTR, and metadata

Resolve upstream input files from the `output_dir` and manifest that `workflow.py` returns for each dependency. Use those locations for inputs in this run.

## Steps

1. Build connected components from nonempty P hashes and known authors, and split the components by a fixed-seed hash.
2. Count all one- to five-word candidates in the discovery split according to the bundled rules. Freeze lists of increases, decreases, previously rare terms, and prespecified watch terms.
3. Open the validation split and calculate differences, ratios, directions, threshold attainment, and component-cluster intervals for each candidate. Keep P, L, and H and the two splits separate.
4. Save results on author coverage, topic and word-count bands, annual MATTR, and the limitations of edit timestamps and inline code boundaries.
5. Independently check for leakage and verify selection ranks, denominators, word boundaries, and validation rows.

## Required Outputs

Save all outputs in the `output_dir` returned by `start`.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `split.csv`
- `candidates.csv`
- `candidate-freeze.json`
- `holdout.csv`
- `vocabulary-spread.csv`
- `mattr.csv`
- `vocabulary-audit.json`

## Completion Criteria

- C01 Known authors and exact nonempty P hashes have zero overlap between the discovery and validation splits.
- C02 The candidate hash is frozen before validation results are opened, and every selection decision and failure to replicate is retained.
- C03 An independent implementation can check original units, sentence and nonword boundaries, the denominator for zero-word P, rarity decisions, watch terms, and insufficient MATTR windows.

Before marking this task complete, have another reviewer independently check the saved outputs and definitions. Verify the receipt criteria, artifacts, and hashes, then record completion with `workflow.py finish` from the project root. Completion requires the full run.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [a04-settings.json](../references/a04-settings.json)

## Interpretation

- Report agreement in the direction of point estimates separately from statistical significance.
- Keep the prespecified thresholds when fewer candidates qualify.
- Limit the exact-duplicate conclusion to exact P matches.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current status.
