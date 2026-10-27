---
name: "ds-resources"
description: "Use when planning work with material disk or concurrency costs, or diagnosing resource pressure."
---

# Resource-aware execution

Use project resource rules and wrappers first. Confirm `/Volumes/Scratch` is mounted; stop disposable-output work if missing, without falling back to Data.

Resolve the installed skill symlink to its repository, then run:

```sh
python3 <repo>/scripts/dsstack.py preflight --project NAME --task ID --expected-gib N
```

Use safe single-component names and estimate additional peak disk use. Check once per task/output namespace, repeating when capacity assumptions materially change. Override the reserve only under explicit user or project policy. Preflight checks mount, paths, and capacity without creating directories, reserving space, or scheduling jobs. Resolve a failed check before costly work.

Use reported temporary/report paths for task-owned output. The build path is for new output: preserve warm Rust/Foundry directories across tasks through project wrappers. Without project rules, use `/Volumes/Scratch/<project>/cargo/<worktree>` for Cargo. Isolate concurrent writers; share caches only through supported mechanisms. Budget simultaneous peaks and batch tests sharing a build.

Route targets, captures, raw receipts, logs, clones, and bytecode to Scratch explicitly when wrappers do not. Commit maintained source and short summaries only.

Before authorized cleanup, check explicit paths, ownership, and open processes. Age alone does not prove disuse. Preserve shared caches and others' work; this skill grants no deletion or process-termination authority.
