---
name: "ds-work"
description: "Use when delivering multi-part or long-running work, resuming it, or handing off a change. Covers trackers, goals, and speed or coverage targets."
---

# Finish one item at a time

## Start

- Read project instructions and contribution guidelines (`CONTRIBUTING*` or `CONTRIBUTOR*`) before editing, in forks and local projects alike. Follow the project's architecture, style, tooling, and required checks.
- List the requested deliverables in the project's tracker or a short checklist. Give each an observable done-when check.
- For open-ended targets or work under a goal or stop hook, follow [targets and budgets](references/targets.md).

## Work

- Keep one item in progress. Close it as done, blocked, or dropped before starting another. Finish independent parts of a blocked item and identify what would clear the remainder.
- Record discoveries as follow-ups; include them now only when the current item depends on them. When the user adds work, update the list and finish or park the current item unless told to switch.
- Between items, reread the ask and remove drift. Edit the working tree directly and commit finished items when commits are part of the task.
- For multi-session work, keep a short done/current/next/blocked note. On resume, read it and the git log; reopen completed items only when later changes invalidate them.

## Checks

- Use the fastest covering check while editing. Run slow suites, matrices, end-to-end checks, and benchmarks once after the last edit they cover, including review fixes.
- Rerun a check after a relevant edit or a failure. Keep unaffected passes. Leave CI and release jobs to CI unless the user or project requires local runs.
- During a long job, work on independent items or wait, with updates when something changes. A failed required check blocks completion; an expected difference from the replaced version does not.

## When stuck

- After two failed fixes for the same failure, or repeated edits without progress, stop patching and find the cause with ds-debug or change approach.
- For missing services, credentials, disk, or permissions, try one or two direct fixes, then report the blocker and what clears it. Continue independent work or hand back. Don't fake a missing service to get a pass.

## Finish

- Mark each item done, blocked, dropped, or not started. Remove temporary debug code and task-owned output, and run outstanding required checks.
- Hand off briefly: what changed, checks and results, important gaps, blockers, and follow-ups. Create receipts or evidence reports only when requested by the user or project.
- Stop when the ask and required checks are complete. Review timing and round limits belong to ds-review.

## Parallel workers

Use workers for independent items with separate files. Give each the item, files, done-when check, and stop boundary. Follow project or host worktree rules; workers start no other workers.
