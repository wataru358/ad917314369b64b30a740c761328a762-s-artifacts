# P2-S05 handoff

The task starts pending. Historical research is recorded separately from the current run.

Read this task’s AGENT.md and status.json, then run `python3 workflow.py start P2-S05 --owner <owner-id>` from the root. Complete any outstanding dependencies first.

Pass the 18 decision rows and references to saved values to S06. On resumption, verify the manifest and evidence locally against the original records.

## Resumption log

The operator appends an entry with the owner ID, run_id, attempt, output directory, fixed inputs and hashes, checkpoint, completed steps, pending work, blockers, and the next command. Append to the log when resuming the same attempt.
