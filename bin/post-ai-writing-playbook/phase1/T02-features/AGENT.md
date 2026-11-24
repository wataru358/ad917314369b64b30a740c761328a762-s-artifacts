# T02 Segmentation, features, and metadata

Read the [root rules](../../AGENT.md) and [Phase 1 rules](../AGENT.md) before starting this task.

## Purpose

Measure words, sentences, bold spans, headings, and metadata from the same body projection, and freeze the six primary metrics and secondary metrics.

## Inputs

- T01 cohort.csv and language-review
- T00 extraction.jsonl and frozen extract.py
- HTML archived by D02

Resolve upstream files from the upstream output_dir and manifest returned by workflow.py. Use paths from the current run.

## Steps

1. Save the bundled segmentation.py and frozen controls. Project P/L/U units, owning blocks, sentences, and words using Unicode offsets.
2. Test the included articles from the five candidates and supplement any shortfall with synthetic fixtures. Read the fixed sample with years hidden to diagnose sentence boundaries, words, and evidence for organizations and authors.
3. Reconcile source DOM order with S words for every included article whose SHA-256 hash has been verified. Save H, bold spans, lists, code positions, the six primary metrics, and secondary metrics such as MATTR.
4. Use the t02_metadata_v2.py rules to save single numeric authors, tags, organizations, article-type cues, and sources. Freeze t02-strata-map.json as topic-map.json.
5. Use independent verification to reconstruct the ID set, token types, half-open owner-to-source ranges, M01–M06, bold and link positions, metadata conflicts, and NA reasons.

## Required Outputs

Save all outputs in the output_dir returned by the start command.
- `report.md`
- `manifest.json`
- `verification.json`
- `verify.py`
- `articles.jsonl`
- `metadata.csv`
- `metadata-provenance.jsonl`
- `metrics.csv`
- `secondary-metrics.csv`
- `segmentation.py`
- `fixtures.json`
- `topic-map.json`
- `calibration.json`

## Completion Criteria

- C01 Each included article has one article row, one metadata row, and six primary metric rows.
- C02 S=P+L+U, sentence and word offsets, bold deduplication and denominators, and known author IDs agree with an independent reading.
- C03 Checks cover synthetic examples, fixed samples, and the evidence for v2 metadata. They distinguish zero, NA, no use, and projection failure.
- C04 Downstream tasks can reuse the frozen code, fixtures, and data schema.

Before completion, have a different person independently verify the saved artifacts and definitions. Check the criteria, artifacts, and hashes in the receipt, then run workflow.py finish from the root. Completion requires the full task to pass after the pilot.

## Frozen Rules

- [measurement-spec.md](../measurement-spec.md)
- [analysis-methods.md](../analysis-methods.md)
- [segmentation.py](../references/segmentation.py)
- [t02_structure.py](../references/t02_structure.py)
- [t02_controls.json](../references/t02_controls.json)
- [t02-strata-map.json](../references/t02-strata-map.json)
- [t02_metadata_v2.py](../references/t02_metadata_v2.py)

## Pitfalls

- Use the full S scope for S measures.
- Treat organization handles and author IDs as distinct identifiers.
- Keep inline code outside the S word stream.
- Limit each structure projection failure to its affected metrics.

See [phase1-handoff.md](phase1-handoff.md) for the handoff and [status.json](status.json) for the current state.
