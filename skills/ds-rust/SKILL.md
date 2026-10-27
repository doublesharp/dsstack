---
name: "ds-rust"
description: "Use when changing Rust crate behavior, Cargo features, async lifecycles, or native dependency boundaries in an existing project."
---

# Rust delivery

Use pinned toolchains, Cargo configuration, lockfiles, wrappers, and runtime/dependency choices. Identify the owning crate, features, and smallest test target before compiling.

Add and run a focused failing behavioral test, implement, then rerun the same target. Repair compiler, fixture, native-library, or command failures first. Batch related cases in existing unit modules or integration binaries; each new `tests/*.rs` adds compilation/linking. A minimal compilable API stub can expose behavioral RED.

`cargo check` proves selected compilation, not test execution, all linking, or native/runtime behavior. Use integration tests across process, database, FFI, cancellation, or resource-lifetime boundaries. Copied/mapped checks prove only that source arrangement.

Reuse compatible artifacts. Prefer the Scratch-routing wrapper; otherwise set a worktree-keyed Scratch `CARGO_TARGET_DIR` and keep it warm across tasks. Isolate writable targets for parallel builds. Keep profile, features, target triple, and `RUSTFLAGS` stable in the inner loop; reuse artifacts only for compatible source, compiler, and environment. Preserve incremental/cache settings; sccache need not cache linking or incremental workloads. Run `cargo clean` or `cargo update` only when required by the task.

Run the broader required gate once at integration; expand workspace/feature coverage when the changed contract or repository policy requires it. Report tested crate/features and distinguish source, linked-artifact, native-service, and runtime evidence.
