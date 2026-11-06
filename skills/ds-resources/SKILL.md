---
name: "ds-resources"
description: "Use when creating a worktree, planning work with large disk or concurrency costs, or diagnosing resource pressure."
---

# Disk and build capacity

Use the user's, project's, or host's worktree and output locations. Keep work in progress in durable storage and disposable builds, caches, logs, and captures in the configured output area. A clone you will edit is work in progress. If a required volume is unavailable, stop the affected writes instead of choosing another disk.

Before a large build or capture, estimate peak space and check capacity with the project's wrapper. If none exists, resolve this skill's installed link to its stack or bundle root and run:

```sh
python3 <root>/scripts/dsstack.py preflight --scratch OUTPUT_ROOT --project NAME --task ID --expected-gib N
```

Use `--profile PATH` for configured limits and output settings; an assembled bundle can provide `profiles/default.json`. Use the configured reserve rather than inventing a lower one to fit. The check validates paths and capacity without creating directories or scheduling builds. Repeat only when the estimate or available capacity changes enough to affect admission. Stop and report a shortfall.

Reuse project output routing; otherwise use the task paths printed by preflight. Keep Rust and Foundry builds warm per worktree. Give concurrent builds separate targets and respect the configured concurrency limits.

Clean only output this task owns, after checking paths and open processes. Leave shared caches and other agents' work alone.
