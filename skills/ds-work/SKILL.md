---
name: "ds-work"
description: "Use when delivering multi-part or long-running work, such as a tracker, a goal, or a multi-session task; when resuming it; or when wrapping up a change for handoff."
---

# One item at a time

## Start

- List the ask as short items, in the project's tracker if it has one. Give each a done-when check you can observe, such as a passing test or a command's output.
- For optimization asks like "make it faster" or "raise coverage", choose a metric, a baseline, a target, and a budget. Stop at the target, at the budget, or after two attempts that don't move the number. If run-to-run noise hides the gain, say so instead of building a better benchmark.
- Ask only when the answer changes what you build and the repo can't tell you. Otherwise pick the reasonable option, say which, and keep going.

## Loop

- Keep one item in progress. Close it as done, blocked, or dropped before starting another.
- Add discovered work to the list as a follow-up. Do it now only if the current item can't finish without it.
- When the user adds or reorders work, update the list and finish or park the current item, unless they say to switch now.
- Between items, reread the original ask and drop anything that drifted from it.
- Edit the working tree directly, not through patch files. Commit each finished item when commits are part of the task.
- For multi-session work, keep a short progress note of done, current, next, and blocked items. On resume, read it and the git log, then continue. Finished items stay finished unless later edits touched their code.

## Checks

- While editing, use the fastest check that covers the change, and close the item when its done-when check passes.
- Run slow or broad checks, such as full suites, matrices, end-to-end runs, and benchmarks, once, after the last edit they cover. If review fixes or later items will touch the same code, wait.
- Rerun a check only after a relevant edit or a failure. A pass holds until you change something it covers.
- Leave CI and release jobs to CI unless the user or project wants them run locally.

## When stuck

- After two failed fixes for the same failure, stop patching. Find the cause with ds-debug or change approach.
- If you're rereading or re-editing the same files without progress, stop and rethink.
- For environment trouble like missing services, credentials, disk, or permissions, try one or two direct fixes, then stop. Report the blocker and what would clear it, and move to items that don't need it or end the turn. Don't fake a missing service to get a pass.

## Finish

- Mark every item done, blocked, dropped, or not started. Remove debug code and temporary files, and keep the diff to the ask.
- Run any required check that hasn't passed since the last edit it covers.
- Hand off in a few lines: what changed, what you ran and the result, anything important you couldn't run, blockers, and follow-ups. Commits, the list, and that message are the record. Don't create receipts, manifests, hashes, or evidence reports unless the user or project asks for them.
- Then stop. Don't keep polishing, and don't add reviews beyond the ones ds-review calls for.

## Parallel workers

Use workers only for independent items that touch separate files. Give each one item, its done-when check, its files, and where to stop. Workers don't start other workers.
