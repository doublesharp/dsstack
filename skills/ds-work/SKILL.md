---
name: "ds-work"
description: "Use when coordinating multi-part or long-running delivery, resuming or handing off tasks, or setting targets and budgets for open-ended work."
---

# Finish one item at a time

- Read project instructions and contribution guidelines. Before running commands in a new worktree, verify its setup prerequisites and working directory; use the project's setup and launch commands. Locate owning files and existing shared code with `rg --files` before path-specific reads; reuse it. Use the project's tools, tracker, and required checks.
- Turn the ask into deliverables with observable done-when checks. Keep one item in progress; record discoveries as follow-ups unless the current item depends on them. When the user changes priorities, update the list and finish or park the current item.
- For open-ended improvement or host goals, set a metric, target, and budget using [targets and budgets](references/targets.md).
- On resume, read the handoff and Git state. Reuse passing results that still cover the same files and environment. If an inherited completion claim lacks a supporting result, check only what the next item relies on.
- While editing, run the fastest covering check. Run slow required checks after the last edit they cover; keep unaffected passes. Leave CI-only jobs to CI unless the project or user requires local runs.
- After two failed fixes for the same failure, recheck the cause and change approach. For missing services, credentials, disk, or permissions, try one or two direct fixes, then report what clears the blocker. Finish independent parts without faking the missing service.
- Keep multi-session notes to done, current, next, and blocked work. Commit completed items when commits are part of the task.
- Give independent workers separate files, an observable outcome, and a stop boundary. They start no nested workers.
- At handoff, account for every requested item. Check ownership and active processes before retiring completed task worktrees and unused build, Docker, and temporary resources; preserve shared resources, deliverables, and unmerged work. Report changes, checks, blockers, and follow-ups briefly. Create evidence reports only when requested. Stop when the ask and required checks are complete.
