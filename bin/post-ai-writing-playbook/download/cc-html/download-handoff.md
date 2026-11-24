# D02 handoff

This task starts as not_started for the new run.

Start by reading this leaf's AGENT.md and status.json, then run `python3 workflow.py start D02 --owner <owner-ID>` from the root. If a dependency is incomplete, return to that task first.

Before resuming, check not_before and the unprocessed ordinal. Hand the evidence of successful acquisitions and all rows, including failures, to Phase 1 T00.

## Resumption log

The assigned agent appends the owner ID, run_id, attempt, output location, frozen inputs and hashes, checkpoint, completed and pending operations, blockers, and the next command here. Keep previous entries when returning to the same attempt.
