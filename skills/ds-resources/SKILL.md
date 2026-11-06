---
name: "ds-resources"
description: "Use when creating a worktree, planning work with large disk or concurrency costs, or diagnosing resource pressure."
---

# Disk and build capacity

Use configured worktree and output locations through the host-authorized write route; disk policy does not grant filesystem access. Worktrees and edited clones belong in durable storage; disposable builds, caches, logs, and captures belong in the output area. If a required volume is unavailable, stop affected writes instead of choosing another disk.

Before a large build or capture, estimate peak space and check capacity with the project's wrapper. Otherwise resolve this skill's installed directory and run its [preflight helper](scripts/preflight.py):

```sh
python3 <skill>/scripts/preflight.py --project NAME --task ID --expected-gib N
```

When present, the bundled profile selects the output root and limits. Use `--profile PATH` for an external profile; pass `--scratch PATH` only when no profile selects a root. Preflight validates paths and capacity without creating directories or scheduling builds. Repeat when changed estimates or capacity could alter admission. Report a shortfall; don't lower the configured reserve to fit.

Reuse project output routing; otherwise use the task paths printed by preflight. Use available sccache for supported Rust, C/C++, and CUDA/HIP compilation through the project's wrapper or compiler launcher. Keep shared compiler caches separate from worktree output, give concurrent builds separate targets, and preserve warm artifacts. Respect configured concurrency limits. When enabling or diagnosing caching, compare `sccache --show-stats` before and after a build; configuration alone doesn't prove reuse.

When work finishes or a worktree is superseded, reclaim unused task-owned resources using the [cleanup procedure](references/cleanup.md). Preserve active/shared resources, requested deliverables, and unmerged work.
