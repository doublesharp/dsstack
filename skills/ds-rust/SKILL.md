---
name: "ds-rust"
description: "Use when changing Rust crate behavior, Cargo features, async lifecycles, or native dependency boundaries in an existing project."
---

# Rust changes

- Use the project's toolchain pin, lockfile, wrappers, and runtime. Find the owning crate and smallest test target before building.
- Run that target through the project wrapper, for example `cargo nextest run -p <crate> <filter>` when nextest is installed. Add cases to existing modules: each new `tests/*.rs` file creates another binary to compile and link.
- Keep the configured target directory, profile, features, target triple, and `RUSTFLAGS` stable to reuse builds. Give concurrent builds separate targets. Use `cargo clean` or `cargo update` only when the task needs it.
- `cargo check` compiles; it doesn't run tests or link everything.
- Use integration tests for process, database, FFI, cancellation, or resource-lifetime boundaries. Include affected dependents or feature combinations when changes cross crate or feature boundaries.
