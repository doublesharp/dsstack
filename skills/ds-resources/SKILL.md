---
name: "ds-resources"
description: "Use when planning work with material disk or concurrency costs, or diagnosing resource pressure."
---

# Resource-aware execution

Read the project's resource rules and use its existing wrappers before adding environment overrides. Confirm that `/Volumes/Scratch` is mounted; if it is unavailable, stop work that would create disposable output instead of falling back to the internal Data volume.

For dsstack's admission check, resolve the installed skill symlink to its repository and run:

```sh
python3 <repo>/scripts/dsstack.py preflight --project NAME --task ID --expected-gib N
```

Choose safe single-component project/task names, estimate additional peak disk use, and retain the project's reserve. Run preflight once per task or new output namespace; repeat if capacity assumptions materially change, rather than before every command. Override the reserve only when project instructions or an explicit user policy require it. Preflight is read-only: it creates nothing. It checks mount, free space, and output-path safety; a nonzero result blocks the proposed costly work until the reported problem is resolved. Use its reported temporary and report paths for task-owned output. The build path is for new task-owned output: preserve existing warm Rust or Foundry directories across tasks through the project wrapper. Without a project rule, key Cargo targets by worktree at `/Volumes/Scratch/<project>/cargo/<worktree>`; isolate concurrent writers. Recommendations about parallelism are advisory; preflight neither schedules jobs nor reserves capacity.

Keep build outputs, captures, raw receipts, logs, cloned fixtures, and bytecode on Scratch. Set the tool's output option or project-supported environment variable explicitly when no wrapper already does so. Keep only maintained source and short human-written summaries in git.

Use a distinct owned target/output directory when concurrent jobs could mutate the same files. Share a cache only through a tool-supported safe mechanism; do not race two writers in a shared Cargo target. Estimate current simultaneous peaks before starting another expensive job, and prefer batching related tests within one crate/target to repeated compilation.

Before cleanup, identify explicit task-owned paths and check ownership plus open processes. Remove superseded disposable outputs only within existing authorization. Age alone does not establish ownership or disuse. Leave shared caches and other tasks' outputs intact. dsstack has no cleanup command or background scheduler; this skill supplies no deletion or process-termination authority.
