# Reproduce post-ai-writing in a new run

Give the prompt in [START.md](START.md) to an AI that can work with files and run commands. Follow the three levels of instructions to acquire the data, run the first comparison, and compare with 2026. Track progress in `status.json`.

```text
AGENT.md / AGENTS.md / START.md / status.json
├── download/AGENT.md / download-handoff.md / status.json
│   ├── cc-index/AGENT.md / download-handoff.md / status.json
│   ├── cc-html/AGENT.md / download-handoff.md / status.json
│   └── dev-api-2026/AGENT.md / download-handoff.md / status.json
├── phase1/AGENT.md / phase1-handoff.md / status.json
│   └── 18 leaf tasks, T00–T03, A01–A12, V01, and R01
└── phase2/AGENT.md / phase2-handoff.md / status.json
    └── 6 leaf tasks, P2-S01–P2-S06
```

The work is organized into a root, branches, and leaf tasks. Specifications, reference implementations, and run artifacts live in separate locations. At every level, `AGENT.md` gives execution rules, the handoff records where to resume, and `status.json` contains Ralph-style `user_stories`, `acceptance_criteria`, and `passes` fields. Parent status is aggregated automatically from leaf tasks. The playbook ships with all 27 leaf tasks marked `not_started` for a fresh run.

## Check the setup

Use Python 3.11 or later on macOS or Linux. Check `python3 --version` and choose an available interpreter such as `python3.11` if the default is too old. Use that interpreter for the commands below. The workflow tracker and example use only the standard library. For the analysis, install and pin any required dependencies in a dedicated environment.

```bash
python3 selftest.py
python3 example_measure.py
python3 workflow.py validate
python3 workflow.py next
```

The self-test uses a temporary directory to check dependencies, ownership, resumption after interruption, rejection of completion without evidence, tamper detection, parent status aggregation, and reloading after a move. It uses synthetic data and leaves current study status untouched. `example_measure.py` uses two fictional articles to illustrate phase-specific denominators, zero, and NA in a small calculation. Full article extraction is outside the example's scope.

## Manage task status

The normal progression is `not_started → in_progress → complete`. Use `blocked` when work cannot proceed, then `retry` after the blocker is resolved. A repeated `start` by the same owner resumes the same attempt. A second owner cannot start that task concurrently. Confirm that the previous owner has stopped before retrying. Use a separate run or copy to recalculate or reset completed tasks.

```bash
python3 workflow.py init --run-id 20261124-dev-writing-v1
python3 workflow.py start D01 --owner controller-1
python3 workflow.py status
python3 workflow.py block D01 --reason 'Reached the connection limit and recorded when to resume'
python3 workflow.py retry D01 --reason 'Confirmed the previous owner stopped and the limit was lifted'
python3 workflow.py sync
```

Initialization seals `config.json` and `schedule.json` in `run-lock.json`. Use a separate run for changes to settings or criteria. If initialization is interrupted, rerun `init` with the same `run_id`.

Read per-chunk time, transfer, and request limits from `config.json`. Probe about five records before processing the full set. Mark a task complete only after processing its full scope. To verify compliance with a transfer limit, measure received bytes.

The `finish` command reads `receipt.json` from the leaf's `output_dir`. See [receipt-guide.md](receipt-guide.md) for the schema and an example. The receipt needs all required outputs and hashes, evidence for every criterion, an independent reviewer, and successful verification. Keep the substance of the independent review because the CLI cannot assess statistical validity. Task completion records that the work was performed. Evidence for an increase or an AI effect is assessed separately.

## Reproduce the method or match historical numbers

The default is to reproduce the method. The original comparison uses 2018–2021 versus 2023–2024. Phase 2 compares January through October (UTC) in 2018–2022 with the same months in 2026. Keep the definitions, weights, author splits, handling of missing data, and verification methods, and record the new results.

Matching historical numbers exactly requires the same snapshot, legacy article ID mapping, input order, code and dependency versions, actual model used for AI classification, and saved decisions. Even with the same seed, new path-hash IDs can produce a different sample from legacy SQLite IDs. Article edits and deletions and changes in the API listing can also affect the results. The original environment's absolute paths are unnecessary for execution.

Package creation left the research unstarted and involved no publishing, pushing, or deployment. Save raw articles in the new run outside the distributed package.

The creation-time checks are recorded in [verification.json](verification.json) and the [42 execution checks](verification-selftest.json). They cover the original playbook and workflow tracker. The review hashes refer to the files as reviewed before translation.
