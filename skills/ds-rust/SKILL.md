---
name: "ds-rust"
description: "Use when changing Rust crate behavior, Cargo features, async lifecycles, or native dependency boundaries in an existing project."
---

# Rust changes

- Use the project's toolchain pin, lockfile, wrappers, and runtime choices. Find the owning crate and its smallest test target before building anything.
- Run that target in the inner loop, for example `cargo nextest run -p <crate> <filter>` through the project wrapper. Add cases to existing test modules. Each new `tests/*.rs` file is another binary to compile and link.
- Keep builds warm. Use the wrapper's Scratch target directory, or `/Volumes/Scratch/<project>/cargo/<worktree>` when there is no wrapper. Keep the profile, features, target triple, and `RUSTFLAGS` the same between runs. Run `cargo clean` or `cargo update` only when the task needs it. Give parallel builds separate target directories.
- `cargo check` compiles. It doesn't run tests or link everything.
- Use integration tests when the change crosses a process, database, FFI, cancellation, or resource-lifetime boundary.
- Run workspace-wide or all-features builds once at the end, and only when the change crosses crates or features or the project requires it.
