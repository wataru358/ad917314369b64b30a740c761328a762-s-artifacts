# P2-S01 handoff

The task starts pending. Historical research is recorded separately from the current run.

Read this task’s AGENT.md and status.json, then run `python3 workflow.py start P2-S01 --owner <owner-id>` from the root. Complete any outstanding dependencies first.

Pass the input index and plan to S02. On resumption, check the plan and input hashes against the original records.

## Resumption log

The operator appends an entry with the owner ID, run_id, attempt, output directory, fixed inputs and hashes, checkpoint, completed steps, pending work, blockers, and the next command. Append to the log when resuming the same attempt.
