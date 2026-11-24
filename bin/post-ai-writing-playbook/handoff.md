# Parent handoff

The new reproduction run has yet to start. Begin at `START.md`. The configured `run_id` is unset and all 27 leaf tasks are `not_started`.

Run the self-test and validation first, then `init` and `next`. After that, use the `resume` and `ready` entries from `workflow.py next`, the leaf handoff, and saved artifacts to decide where to continue.

## What to record after execution

Record the `run_id`, frozen configuration and specification hashes, current owner and attempt, completed and pending work, blockers, and the next action. Label historical statistical judgments and new-run judgments separately.
