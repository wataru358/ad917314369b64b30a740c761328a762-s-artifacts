# Phase 1 — Comparing English DEV articles

Use archived DEV articles to measure differences in writing length, sentence rhythm, and formatting between 2018–2021 and 2023–2024. Explore changes in vocabulary, voice, structure, descriptions of concrete material, and article composition, and examine their timing. Summarize how results vary by condition in Japanese editorial materials.

## Start or resume

1. Read the [root instructions](../AGENT.md) and [resumption steps](phase1-handoff.md). Check the run profile and evidence that D02 is complete.
2. Read the [measurement specification](measurement-spec.md) and [analysis methods](analysis-methods.md). Use the current run to establish counts and results.
3. Run `python3 workflow.py next` at the package root. Open the selected leaf task's instructions and work in the attempt directory returned by `python3 workflow.py start ID --owner NAME`.
4. Resolve the accepted attempt paths for this run and its dependencies from status and verify SHA-256 hashes against the files. Give each leaf task exclusive write access to its products and working files.
5. Finish implementation, measurement, and independent verification. Have a different person check the inputs and artifacts directly and record the scope of that review in `verification.json`.
6. Record the run ID, task ID, attempt, profile, evidence for each acceptance criterion, and artifact SHA-256 hashes in `receipt.json`. Run `python3 workflow.py finish ID --evidence <relative-path-to-receipt>`.

Even for the full profile, first complete extraction, classification, saving, and readback on the five fixed candidates. After verifying those five, continue with all frozen inputs. Leave the attempt in progress after a probe-only run and record the scope of verification in the checkpoint.

## Dependencies

| Task | Direct dependencies |
| --- | --- |
| T00 / T01 / T02 / T03 | D02 / T00 / T01 / T02, respectively |
| A01–A05, A08 | T03 |
| A06 | T03, A04 |
| A07 | T03, A05 |
| A09 | A01–A08 |
| A10 | A01, A02, A03, A09 |
| A11 | T03, A06, A07, A08 |
| A12 | T03, A01, A02, A03, A05, A09 |
| V01 | A01–A12 |
| R01 | T03, A01–A12, V01 |

After T03, run A01–A05 and A08 in parallel. Start A06 after A04 and A07 after A05. Run A09, A10, A11, and A12 as their direct dependencies become available. V01 compares results under different conditions, and R01 finalizes the Japanese editorial materials.

Report the years, article and known-author counts, reasons for any unavailable calculations, units, and population for every comparison. Distinguish exploratory analyses from primary comparisons. Save the specified rows with reasons when support is insufficient. Keep execution blockers and implementation failures open as such. Store article text, blinded ID mappings, and excerpts in local run artifacts.
