---
name: "ds-rust"
description: "Use when changing Rust crate behavior, Cargo features, async lifecycles, or native dependency boundaries in an existing project."
---

# Rust changes

- Reuse the toolchain pin, lockfile, wrappers, runtime, and shared crate utilities. Consolidate duplication the change touches; leave intentionally different behavior and unrelated code alone. Find the owning crate and smallest existing test target before building.
- Run that target through the wrapper, for example `cargo nextest run -p <crate> <filter>` when installed; `cargo check` neither runs tests nor links everything. Add cases to existing modules: each new `tests/*.rs` file creates another binary to compile and link.
- Before changing build setup, run `command -v cargo-steward`. When present, it is Cargo's rustc wrapper with sccache behind it and may route each worktree's target and `TMPDIR`; follow the installed `cargo-steward` skill. Don't set your own `RUSTC_WRAPPER` (even empty), `CARGO_TARGET_DIR`, or `--target-dir`; they bypass or reroute it. Pick its inner wrapper with `CARGO_STEWARD_INNER`, and see where a build goes with `cargo steward shim explain`.
- Without cargo-steward, use available sccache through the project wrapper or `RUSTC_WRAPPER=sccache`, preserving existing wrapper chains, and give concurrent builds separate targets.
- Set `CARGO_INCREMENTAL=0` for cacheable builds; incremental rustc output is not cacheable. Preserve an explicitly required incremental workflow. When enabling or diagnosing caching, compare `sccache --show-stats` before and after a real build.
- Keep the target directory, profile, features, target triple, and `RUSTFLAGS` stable. Don't clean warm output just to demonstrate cache hits.
- Use all available logical CPU cores. If config or wrappers lower Cargo jobs or test threads through `CARGO_BUILD_JOBS`, `RUST_TEST_THREADS`, or nextest's `--test-threads`, set them to the detected count. Keep tests serial only where the project requires isolation.
- Use integration tests for process, database, FFI, cancellation, or resource-lifetime boundaries. Include affected dependents or feature combinations when changes cross crate or feature boundaries.

When a task/worktree is complete or superseded, remove its unused targets and temporary output. With cargo-steward, run `cargo steward remove --worktree <dir>` to preview, then again with `--apply`, before deleting the worktree; free space with `cargo steward gc` rather than `cargo clean` or deleting build files. Without it, check active processes first. Preserve shared caches, required artifacts, and unmerged work.
