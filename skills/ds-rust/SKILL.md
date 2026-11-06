---
name: "ds-rust"
description: "Use when changing Rust crate behavior, Cargo features, async lifecycles, or native dependency boundaries in an existing project."
---

# Rust changes

- Reuse the toolchain pin, lockfile, wrappers, runtime, and shared crate utilities. Consolidate duplication the change touches; leave intentionally different behavior and unrelated code alone. Find the owning crate and smallest existing test target before building.
- Run that target through the wrapper, for example `cargo nextest run -p <crate> <filter>` when installed. Add cases to existing modules: each new `tests/*.rs` file creates another binary to compile and link.
- Use available sccache through the project wrapper or `RUSTC_WRAPPER=sccache`, preserving existing wrapper chains. Set `CARGO_INCREMENTAL=0` for cacheable builds; incremental rustc output is not cacheable. Preserve an explicitly required incremental workflow. When enabling or diagnosing caching, compare `sccache --show-stats` before and after a real build.
- Keep the target directory, profile, features, target triple, and `RUSTFLAGS` stable. Give concurrent builds separate targets; don't clean warm output just to demonstrate cache hits.
- Use all available logical CPU cores. If config or wrappers lower Cargo jobs or test threads through `CARGO_BUILD_JOBS`, `RUST_TEST_THREADS`, or nextest's `--test-threads`, set them to the detected count. Keep tests serial only where the project requires isolation.
- `cargo check` compiles; it does not run tests or link everything.
- Use integration tests for process, database, FFI, cancellation, or resource-lifetime boundaries. Include affected dependents or feature combinations when changes cross crate or feature boundaries.

When a task/worktree is complete or superseded, remove its unused targets and temporary output after checking active processes. Preserve shared caches, required artifacts, and unmerged work.
