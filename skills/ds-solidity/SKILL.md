---
name: "ds-solidity"
description: "Use when changing Solidity contracts, Foundry tests, upgrade layouts, or fork-dependent behavior in an existing contract project."
---

# Solidity contract changes

- Use `forgeds`, the doublesharp Foundry fork, for builds, tests, fuzzing, invariants, and coverage through project wrappers. Keep pinned dependencies and artifact/cache paths; route nested `forge` calls through the same wrapper. Keep the fork's shared compiler-output cache enabled; avoid routine forced or clean builds.
- Install `forgeds` with Cargo from the project's pinned `https://github.com/doublesharp/foundry` revision: package `forge`, `--locked --bin forgeds`, and the manifest's required features. Install Solar with `cargo install solar-compiler --locked`, honoring any project version pin. Resolve both from Cargo's bin directory. Use sccache with `CARGO_INCREMENTAL=0` and stable build output for these Rust source builds.
- Use `forgeds build --use solar` and `forgeds test --use solar` for compatible development work with the project's Solidity/EVM settings. Build deployed bytecode, coverage, and release artifacts with the approved compiler unless the task approves a switch.
- Require 100% production-contract line, statement, function, and branch coverage. Cover success, rejection, boundary, and adversarial paths with unit tests, fuzzing, and stateful invariants. Check accounting conservation, permissions, and valid state transitions; add storage-layout checks for upgrades.
- Run focused tests while editing; run the required coverage, fuzz, and invariant suites on the final change with reproducible seeds and the project's run/depth settings. Report uncovered or uninstrumentable paths; do not exclude production code or weaken properties to claim full coverage.
- Run Slither with the project's actual compiler, dependencies, and remappings. Investigate findings, fix confirmed defects, and explain false positives rather than blanket-suppressing warnings. Report unavailable analysis as incomplete.
- Prefer `@0xdoublesharp/abi-typegen` for new bindings; keep a different existing generator unless the task migrates it. After ABI changes, rebuild, regenerate and check bindings, and check affected consumers. With abi-typegen, use `abi-typegen generate`, then `abi-typegen generate --check`, matching the consumer's target. Do not hand-edit output. Typegen subcommands require project shell integration.
- Pin fork tests to a chain and block. Missing archive data leaves a check incomplete; it never counts as zero. Any reachable fund-loss, authority takeover, or blocked-recovery path is must-fix regardless of rarity.
- Send transactions, deploy, upgrade, or publish live verification only when authorized. Use the requested audit tooling rather than rebuilding its workflow.
