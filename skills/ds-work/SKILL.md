---
name: "ds-work"
description: "Use when delivering multi-part or long-running work, like a tracker, a goal, a speed or coverage target, or a multi-session task; when resuming it; or when handing off a change."
---

# One item at a time

## Start

- List the ask as short items, in the project's tracker if it has one. Give each a done-when check you can observe, like a passing test or a command's output.
- For open-ended asks like "make it faster", and under any goal or stop hook, follow [references/targets.md](references/targets.md).
- In forks and local projects, read project instructions and contribution guidelines (`CONTRIBUTING*` or `CONTRIBUTOR*`) before editing. Follow project architecture, style, tooling, required checks, and conventions.

## Loop

- Keep one item in progress. Close it as done, blocked, or dropped before starting another.
- If part of an item needs something you can't get, like a real provider or credentials, close the rest and file that part as a blocked follow-up.
- Add discovered work to the list as a follow-up. Do it now only if the current item can't finish without it.
- When the user adds or reorders work, update the list, then finish or park the current item unless told to switch now.
- Between items, reread the ask and drop anything that drifted.
- Edit the working tree directly, not through patch files. Commit each finished item when commits are part of the task.
- For multi-session work, keep a short note of done, current, next, and blocked items. On resume, read it and the git log. Finished items stay finished unless later edits touched their code.

## Checks

- While editing, use the fastest check that covers the change, and close the item when its done-when check passes.
- Run slow checks, like full suites, matrices, end-to-end runs, and benchmarks, once, after the last edit they cover. If review fixes or later items will touch the same code, wait.
- Rerun a check only after a relevant edit or a failure.
- While a long job runs, work on other items or wait quietly, posting only when something changes.
- Only a failed check the ask or project requires is a blocker. Differences from the version you're replacing are expected.
- Leave CI and release jobs to CI unless the user or project wants them run locally.

## When stuck

- After two failed fixes for the same failure, or when you're re-editing the same files without progress, stop patching. Find the cause with ds-debug or change approach.
- For environment trouble like missing services, credentials, disk, or permissions, try one or two direct fixes, then stop. Report the blocker and what would clear it, and move to items that don't need it or end the turn. Don't fake a missing service to get a pass.

## Finish

- Mark every item done, blocked, dropped, or not started. Remove debug code and temporary files, and keep the diff to the ask.
- Run any required check that hasn't passed since the last edit it covers.
- Hand off in a few lines: what changed, what ran and its result, anything important you couldn't run, blockers, and follow-ups. Create receipts, manifests, or evidence reports only when the user or project asks.
- Then stop. Don't keep polishing, and don't add reviews beyond the ones ds-review calls for.

## Parallel workers

Use workers only for independent items that touch separate files. Give each one item, its done-when check, its files, and where to stop. Put their worktrees where ds-resources says. Workers don't start other workers.
