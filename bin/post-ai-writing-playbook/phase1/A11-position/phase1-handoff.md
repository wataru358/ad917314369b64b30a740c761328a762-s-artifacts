# A11 Handoff

This task starts with status `not_started`. Record completion for this run only.

First read this task's `AGENT.md` and `status.json`. From the project root, run `python3 workflow.py start A11 --owner <owner-id>`. If any dependencies are incomplete, return to those tasks first.

Pass separate automated and content tables, unsupported scopes, and counterexamples about absolute versus relative position to V01 and R01. Mark any outstanding reevaluation as required work.

## Progress Log

The task owner appends their owner ID, `run_id`, `attempt`, output location, frozen inputs and their hashes, checkpoint, completed work, pending work, blockers, and the next command. Append to the existing log when resuming the same attempt.
