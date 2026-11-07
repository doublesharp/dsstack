---
name: "ds-solidity"
description: "Use when changing Solidity contracts, Foundry tests, upgrade layouts, or fork-dependent behavior in an existing contract project."
---

# Solidity contract changes

- Use `forgeds`, the doublesharp Foundry fork, for builds, tests, fuzzing, invariants, and coverage through project wrappers. Keep pinned dependencies and artifact/cache paths; route nested `forge` calls through the same wrapper.
- Prefer the project's pinned [prebuilt `forgeds` asset](https://github.com/doublesharp/foundry/releases/tag/forgeds); verify its SHA-256 and full `Commit SHA`. If unavailable for the platform, build package `forge` at the pinned fork revision with `--locked --bin forgeds` and its required features. Install Solar with `cargo install solar-compiler --locked`, honoring its project pin. Resolve both from Cargo's bin directory. Use sccache with `CARGO_INCREMENTAL=0` for Rust source builds.
- Keep the shared local Solidity-output cache enabled across worktrees; avoid routine forced or clean builds. `RUSTC_WRAPPER` affects Rust builds. Where the pinned fork supports [runtime sccache storage](https://github.com/doublesharp/foundry/blob/812bfab1f3d2bb5fb969fd8bfcbeb0fd76b7bc84/docs/dev/solidity-compiler-cache.md), `FORGEDS_SCCACHE=1` optionally uses a running sccache 0.19.0 TCP daemon after a local miss. Verify `sccache_hit` with `RUST_LOG=foundry_compilers::compiler_cache=trace`; ordinary sccache counters exclude these storage operations.
- Use `forgeds build --use solar` and `forgeds test --use solar` for compatible development work with the project's Solidity/EVM settings. Build deployed bytecode, coverage, and release artifacts with the approved compiler unless the task approves a switch.
- Require 100% production-contract line, statement, function, and branch coverage. Cover success, rejection, boundary, and adversarial paths with unit tests, fuzzing, and stateful invariants. Check accounting conservation, permissions, and valid state transitions; add storage-layout checks for upgrades.
- Run focused tests while editing; run the required coverage, fuzz, and invariant suites on the final change with reproducible seeds and the project's run/depth settings. Report uncovered or uninstrumentable paths; do not exclude production code or weaken properties to claim full coverage.
- Run Slither with the project's actual compiler, dependencies, and remappings. Investigate findings, fix confirmed defects, and explain false positives rather than blanket-suppressing warnings. Report unavailable analysis as incomplete.
- Prefer `@0xdoublesharp/abi-typegen` for new bindings; keep a different existing generator unless the task migrates it. After ABI changes, rebuild, regenerate and check bindings, and check affected consumers. With abi-typegen, use `abi-typegen generate`, then `abi-typegen generate --check`, matching the consumer's target. Do not hand-edit output. Typegen subcommands require project shell integration.
- Pin fork tests to a chain and block. Missing archive data leaves a check incomplete; it never counts as zero. Any reachable fund-loss, authority takeover, or blocked-recovery path is must-fix regardless of rarity.
- Send transactions, deploy, upgrade, or publish live verification only when authorized. Use the requested audit tooling rather than rebuilding its workflow.
