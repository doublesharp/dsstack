---
name: "ds-rust"
description: "Use when changing Rust crate behavior, Cargo features, async lifecycles, or native dependency boundaries in an existing project."
---

# Rust changes

- Reuse the toolchain pin, lockfile, wrappers, runtime, and shared crate utilities. Consolidate duplication the change touches; leave intentionally different behavior and unrelated code alone. Find the owning crate and smallest existing test target before building.
- Run that target through the wrapper, for example `cargo nextest run -p <crate> <filter>` when installed; `cargo check` neither runs tests nor links everything. Add cases to existing modules: each new `tests/*.rs` file creates another binary to compile and link.
- Check `command -v cargo-steward` before changing build wrappers, target routing, or cleanup; follow [build caching and cleanup](references/builds.md). Keep `CARGO_INCREMENTAL=0` for cacheable builds, preserve warm targets and existing wrapper chains, and never bypass `cargo-steward` or manually delete managed build output.
- Respect explicit concurrency caps such as `$COMPUTE_JOBS` or project-isolated tests. Otherwise use available logical CPU cores instead of artificially low Cargo or nextest thread defaults.
- Use integration tests for process, database, FFI, cancellation, or resource-lifetime boundaries. Include affected dependents or feature combinations when changes cross crate or feature boundaries.
- When a task or worktree is complete or superseded, reclaim its unused targets and temporary output through [the cleanup rules](references/builds.md), preserving shared caches, required artifacts, and unmerged work.
