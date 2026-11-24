# Acquire DEV articles

Save DEV pages archived by Common Crawl and 2026 articles returned by the DEV API in a form that can be verified again. Read the parent `AGENT.md` and `config.json`, then run `python3 workflow.py next` to find where to resume.

| Task | Input | Handoff |
| --- | --- | --- |
| [D01](cc-index/AGENT.md) | Public `CC-MAIN-2025-43` index | Frozen candidate paths and index file list |
| [D02](cc-html/AGENT.md) | Frozen D01 artifacts | Compressed WARC records, HTML, and the acquisition ledger for all candidates |
| [D03](dev-api-2026/AGENT.md) | DEV API listing and detail responses | Frozen plan by UTC month, raw JSON, and acquisition ledger |

D01 and D03 are independent and can proceed in separate output directories. D02 uses the frozen D01 artifacts for the same `run_id`. All tasks write to the directory returned by `workflow.py start`, `runs/<run_id>/download/<task-id>/<attempt>/`. Downstream tasks resolve the completed attempt's `output_dir` from workflow status.

On the first attempt, read the shared rules and your task's section in the [acquisition specification](download-spec.md). Check the specification and storage format on five records before full acquisition. D01 uses five index candidate rows, D02 uses five frozen candidate records, and D03 uses five listing records for the connection probe and the first five records in the frozen plan. Resume from saved state after a processing limit or wait. Honor server wait deadlines and use the time to work on independent tasks.

Record the five-record check before issuing a completion receipt. Hand off the artifacts after the full-scope criteria are met. Downstream tasks handle English-language classification, body extraction, and eligibility for analysis.

Use the [download handoff](download-handoff.md) to pass on the work. See the [original research materials](provenance.md) for historical counts and sources.
