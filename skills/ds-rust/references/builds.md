# Rust build caching and cleanup

Use these rules when configuring build wrappers, diagnosing compiler cache reuse, or cleaning up Rust targets.

- **With `cargo-steward` (`command -v cargo-steward`):** it wraps `rustc` with `sccache` behind it and may route each worktree's target directory and `TMPDIR`. Follow the installed `cargo-steward` skill. Never set `RUSTC_WRAPPER` (even empty); select an inner wrapper only through `CARGO_STEWARD_INNER`. Inspect routing with `cargo steward shim explain --json`: when `target_dir.routed` is true, do not set `CARGO_TARGET_DIR` or `--target-dir`; otherwise follow the project's target-dir policy.
- **Without `cargo-steward`:** use available `sccache` through the project wrapper or `RUSTC_WRAPPER=sccache`, preserving existing wrapper chains, and give concurrent builds separate targets.
- **Cacheable builds:** set `CARGO_INCREMENTAL=0` because incremental `rustc` output is not cacheable; preserve an explicitly required incremental workflow. Keep the target directory, profile, features, target triple, and `RUSTFLAGS` stable. Compare `sccache --show-stats` before and after an actual build to verify reuse; do not clean warm output just to demonstrate cache hits.
- **Cleanup:** when a task or worktree finishes or is superseded, remove unused targets and temporary output while preserving shared caches, required artifacts, and unmerged work.
  - With `cargo-steward`, preview `cargo steward remove --worktree <dir>`, then run again with `--apply`, before deleting the worktree (`remove --orphaned` covers already-deleted worktrees). Free space with `cargo steward gc` rather than `cargo clean` or manual target deletion.
  - Without `cargo-steward`, check active processes before removing task-exclusive targets.
