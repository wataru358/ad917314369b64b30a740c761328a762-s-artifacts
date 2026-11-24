# T00 Handoff

The initial state is pending. Prior research provides provenance for this run.

First read AGENT.md and status.json for this task, then run `python3 workflow.py start T00 --owner <owner-id>` from the root. If a dependency is incomplete, return to the prerequisite task.

Pass the full candidate ledger, extraction results, probe, and code hashes to T01. Reuse matching shards when resuming partway through.

## Resume Log

The operator adds the owner ID, run_id, attempt, output directory, frozen inputs and hashes, checkpoint, completed operations, outstanding work, blockers, and the next command. Append updates when resuming the same attempt so earlier progress stays recorded.
