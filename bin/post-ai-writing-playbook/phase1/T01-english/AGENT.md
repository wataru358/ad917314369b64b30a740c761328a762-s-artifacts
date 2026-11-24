# T01 Body language classification and English cohort

Read the [root rules](../../AGENT.md) and [Phase 1 rules](../AGENT.md) before starting this task.

## Purpose

Assign a status to every candidate and freeze the analysis cohort based on English body text and UTC publication year.

## Inputs

- T00 extraction.jsonl, input-ledger.csv, pilot.json, and original D02 sources

Resolve upstream files from the upstream output_dir and manifest returned by workflow.py. Use paths from the current run.

## Steps

1. Freeze the bundled language_rules.py as language-rules.py and lock all 75 Lingua languages. Use T00 probe articles to verify that S, P, L, and 1,200-character spans can be saved and read back.
2. Select 20 calibration and 10 validation examples per year and a separate diagnostic sample by hash. Use calibration and diagnostics to check quality when freezing the 0.70 and 0.30 thresholds.
3. Score every candidate automatically. Store manual overrides in a separate column only for evidence-backed full-text decisions from calibration or diagnostics. Save the blinded validation results.
4. Set adopted=true only for English candidates with a UTC publication year from 2018 through 2025. Retain rows that are out of scope, missing a timestamp, mixed, empty, or unavailable.
5. Independently recalculate candidate hashes, complete S span coverage and labels, UTC years, and sample and inclusion totals.

## Required Outputs

Save all outputs in the output_dir returned by the start command.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `cohort.csv`
- `language-evidence.jsonl`
- `language-rules.py`
- `language-settings.json`
- `language-review.json`

## Completion Criteria

- C01 There is exactly one language and inclusion row per candidate. UTC boundaries and counts for all states reconcile.
- C02 Blinded calibration, validation, and diagnostics are separate. The freeze order, sample shortfalls, and evidence for manual overrides are saved.
- C03 The cohort excludes non-English, indeterminate, and out-of-period articles and retains short and identical articles.

Before completion, have a different person independently verify the saved artifacts and definitions. Check the criteria, artifacts, and hashes in the receipt, then run workflow.py finish from the root. Completion requires the full task to pass after the pilot.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [language_rules.py](../references/language_rules.py)

## Pitfalls

- Use html lang, CC language, and tags as hints only.
- Keep English-dominant mixed articles as candidates only.
- Evaluate the validation group independently of manual overrides.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current state.
