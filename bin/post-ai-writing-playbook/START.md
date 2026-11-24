# Prompt to give the AI

```text
Read AGENT.md in this folder and begin a new run of the post-ai-writing study of English-language DEV articles.
Start any work that can proceed.

1. Confirm that you are at the playbook root. From the outer repository, change to bin/post-ai-writing-playbook. Check python3 --version and select a Python 3.11 or later interpreter. Use it for every subsequent python3 command. Run python3 selftest.py and python3 workflow.py validate. The self-test uses only fictional data in a temporary directory and does not run the study. Run sync and rerun validate only if the validation error starts with stale. If validation reports initialization incomplete, rerun init with the existing run_id and then rerun validate. For other integrity errors, examine the cause and saved evidence and report the error.
2. If run_id in config.json is null, choose a new ID that includes the current date and time and set it with python3 workflow.py init --run-id <ID>. Keep any existing ID. Rerunning init with the same ID preserves committed state.
3. Read the output of python3 workflow.py next. For in_progress work, resume from the handoff and checkpoint. If the previous owner is still working, let that owner continue. Use block/retry to move to a new attempt only after confirming the previous owner has stopped. Record the reason.
4. Choose one leaf task from ready whose dependencies are satisfied. Read the branch and leaf AGENT.md files and handoffs. Claim it with python3 workflow.py start <ID> --owner <owner-ID>. Put the code and artifacts in the returned output_dir.
5. Implement the specified rules and check them on a small pilot. Then process the full frozen set in chunks. When a processing limit is reached, continue from the checkpoint in the same attempt. Create missing implementations or inputs where possible and use block with a reason for blockers that cannot be resolved.
6. Have another agent independently verify the work. Record evidence for each acceptance criterion, all required outputs, SHA-256 hashes, and actual verification results in receipt.json. CLI acceptance checks the receipt. Use the independent review to assess the substance.
7. Record completion with python3 workflow.py finish <ID> --evidence <receipt-path-relative-to-root>. Parent progress is aggregated automatically.
8. Return to python3 workflow.py next and continue available work until everything is complete or blockers prevent further progress. Delegate within the available concurrency slots and assign disjoint files to concurrent agents.
9. Before pausing, update the handoff and run python3 workflow.py sync and validate. Briefly report completed work, pending work, blockers, the next action, and what the current results support.

Preserve source data and existing runs. Base acceptance on the planned method and verification, regardless of whether historical numbers match.
Keep the time windows, metrics, denominators, and formal judgments for Phase 1 and Phase 2 distinct.
If the new corpus differs from the original artifacts, record the differences as part of the new method reproduction.
```

Use the same prompt to resume. The model needs access to the local files, commands, and any network resources required by the study. Run this prompt in an active session. This file contains the prompt and does not schedule jobs or start a background agent.
