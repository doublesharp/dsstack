---
name: "ds-rust"
description: "Use when changing Rust crate behavior, Cargo features, async lifecycles, or native dependency boundaries in an existing project."
---

# Rust delivery

Use the repository's pinned toolchain, Cargo configuration, lockfile, and command wrappers. Identify the owning crate, relevant features, and smallest test target before compiling. Preserve the project's runtime and dependency choices.

For behavioral changes, add the smallest meaningful failing test and run that crate/test target. Batch related cases in the same target so a single compile exercises the change. RED means the expected behavioral assertion failed; compiler errors, missing native libraries, and missing commands require fixture or environment repair first. Then implement the change and rerun the same target.

`cargo check` proves compilation under its selected configuration; it does not execute tests, link every artifact, or establish native/runtime behavior. Select integration tests when behavior crosses process, database, FFI, cancellation, or resource-lifetime boundaries. A copied or mapped source check proves only that source arrangement.

Reuse valid artifacts for the same source, compiler, features, and relevant environment. Prefer the existing wrapper that routes build output to Scratch; otherwise set an explicit Scratch `CARGO_TARGET_DIR`. Parallel builds need isolated writable target directories. Preserve working incremental and cache settings; sccache is not a promise to cache linking or incremental workloads.

At integration, run the broader required gate once. Expand to workspace tests or feature combinations when the changed contract or repository policy calls for them; do not repeat a workspace feature matrix after each small edit. Report the exact tested crate/features and keep source, linked artifact, native service, and runtime evidence distinct.
