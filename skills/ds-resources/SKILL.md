---
name: "ds-resources"
description: "Use when planning work with large disk or concurrency costs, or diagnosing resource pressure."
---

# Disk and build capacity

Follow project wrappers and resource rules first. If `/Volumes/Scratch` isn't mounted, stop any work that writes disposable output and say so. Don't fall back to the Data volume.

Before a large build or capture, resolve this skill's installed symlink to its repository and run the preflight once for the task:

```sh
python3 <repo>/scripts/dsstack.py preflight --project NAME --task ID --expected-gib N
```

Names may use letters, digits, dots, hyphens, and underscores. The preflight checks the mount, the output paths, and free space against your estimated peak plus the reserve, and it creates nothing. Run it again only if your size estimate changes a lot, and use a different reserve only when the user or project sets one. If space is short, stop and tell the user what you need instead of reworking the build to fit.

When wrappers don't route output, put targets, captures, logs, reference clones, and bytecode under the Scratch paths the preflight prints. Keep worktrees and any clone you edit on the backed-up Data volume, never on Scratch. Keep Rust and Foundry targets warm per worktree across tasks. Without a project rule, Cargo uses `/Volumes/Scratch/<project>/cargo/<worktree>`. Give concurrent builds separate target directories, and don't start a second heavy build from the same task while one is running.

Clean up only output this task created, after checking the paths and that no process has them open. Leave shared caches and other agents' work alone.
