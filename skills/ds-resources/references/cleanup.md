# Reclaim task resources

At completion, cancellation, or replacement, identify resources this task created and release those no longer needed. Confirm exact paths, ownership, active processes, and dependencies first. Keep requested deliverables and recovery material still needed.

- **Worktrees:** check Git status and whether work is merged or saved. Remove clean, completed task worktrees with `git worktree remove`; delete merged task branches with `git branch -d`. Preserve unmerged work unless discarding it is authorized.
- **Builds and temp:** remove obsolete task targets, coverage, test fixtures, captures, and temporary files. Keep warm artifacts while a task/worktree needs them; do not clean shared caches or another task's targets.
- **Docker:** stop and remove task-owned containers and networks. Remove unused task images and disposable task volumes only after confirming no running or retained workload needs them. Do not run global prune commands or remove persistent user data.
- **Local AI:** stop task-started model servers or unload idle task models. Remove task-only downloads, inference caches, and generated datasets when unused; preserve shared model libraries and user-selected models.

Use scoped removal commands through the host-authorized execution route. Check reclaimed space when disk pressure motivated cleanup. State any resource retained because it is still needed.
