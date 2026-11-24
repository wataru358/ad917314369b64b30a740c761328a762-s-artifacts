# T00 Freeze the inputs and execution conditions

Read the [root rules](../../AGENT.md) and [Phase 1 rules](../AGENT.md) before starting this task.

## Purpose

Freeze the candidate set, source HTML, extraction rules, and execution environment, then create an extraction ledger for all candidates.

## Inputs

- D02 acquisitions.jsonl, manifest, summary, verification, and HTML for successful rows

Resolve upstream files from the upstream output_dir and manifest returned by workflow.py. Use paths from the current run.

## Steps

1. Connect to the accepted D02 attempt in read-only mode. Copy candidate IDs, URLs, dates, HTML references, and sources into the ledger.
2. Freeze the bundled extractor as extract.py. Record Python, lxml, libxml, locale and UTC settings, and dependency installation instructions.
3. Run a small extraction on the five fixed D02 candidates. Independently check the body selector and its correspondence to the source HTML.
4. Apply the same code to every candidate. Record success, acquisition failure, missing or ambiguous body, and decoding or parsing failure. Keep empty S among the successful extractions.
5. Use an independent implementation to check input and shard SHA-256 hashes, uniqueness, the ID set, and edge cases.

## Required Outputs

Save all outputs in the output_dir returned by the start command.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `input-ledger.csv`
- `extraction.jsonl`
- `extract.py`
- `environment.json`
- `pilot.json`

## Completion Criteria

- C01 Candidate IDs are unique, and all acquisition states and HTML hashes match D02.
- C02 The five-candidate probe and synthetic negative cases distinguish acquisition failures, extraction failures, and empty S.
- C03 Every candidate has an extraction state, and all exclusions are accounted for. SHA-256 hashes for the code, environment, and configuration can be verified again.

Before completion, have a different person independently verify the saved artifacts and definitions. Check the criteria, artifacts, and hashes in the receipt, then run workflow.py finish from the root. Completion requires the full task to pass after the pilot.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [article_extraction.py](../references/article_extraction.py)

## Pitfalls

- Use the current run's criteria for inclusion independently of historic counts and run IDs.
- Keep a row for every failed candidate.
- Leave attempts that stop after five candidates in progress.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current state.
