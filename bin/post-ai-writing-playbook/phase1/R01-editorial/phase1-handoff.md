# R01 Handoff

The initial state is pending. Prior research provides provenance for this run.

First read AGENT.md and status.json for this task, then run `python3 workflow.py start R01 --owner <owner-id>` from the root. If a dependency is incomplete, return to the prerequisite task.

Pass the new run's outputs and the Phase 2 input index downstream. Synchronize and validate overall status with the CLI.

## Resume Log

The operator adds the owner ID, run_id, attempt, output directory, frozen inputs and hashes, checkpoint, completed operations, outstanding work, blockers, and the next command. Append updates when resuming the same attempt so earlier progress stays recorded.
