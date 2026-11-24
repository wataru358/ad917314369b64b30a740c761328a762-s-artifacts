# D03 handoff

This task starts as not_started for the new run.

Start by reading this leaf's AGENT.md and status.json, then run `python3 workflow.py start D03 --owner <owner-ID>` from the root. If a dependency is incomplete, return to that task first.

During listing, record the next page. After freezing the plan, record the next unprocessed ID. Once complete, pass plan.jsonl and responses.jsonl to the Phase 2 corpus task.

## Resumption log

The assigned agent appends the owner ID, run_id, attempt, output location, frozen inputs and hashes, checkpoint, completed and pending operations, blockers, and the next command here. Keep previous entries when returning to the same attempt.
