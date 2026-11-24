# A07 Handoff

This task starts with status `not_started`. Record completion for this run only.

First read this task's `AGENT.md` and `status.json`. From the project root, run `python3 workflow.py start A07 --owner <owner-id>`. If any dependencies are incomplete, return to those tasks first.

Pass fixed blinded calibration and evaluation packets and the crosswalk to A11. Pass separate proxy and content outputs to A09 and R01.

## Progress Log

The task owner appends their owner ID, `run_id`, `attempt`, output location, frozen inputs and their hashes, checkpoint, completed work, pending work, blockers, and the next command. Append to the existing log when resuming the same attempt.
