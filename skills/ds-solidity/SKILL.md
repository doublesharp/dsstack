---
name: "ds-solidity"
description: "Use when changing Solidity contracts, Foundry tests, upgrade layouts, or fork-dependent behavior in an existing contract project."
---

# Solidity contract changes

- Use Foundry Forge for builds, tests, fuzzing, invariants, and coverage. Reuse pinned dependencies, configuration, and wrappers; keep artifact/cache paths warm and consistent.
- Use Solar when available for compilation and checks it supports with the project's Solidity/EVM settings. Build deployed bytecode, coverage, and release artifacts with the approved compiler unless the task approves a switch.
- Require 100% production-contract line, statement, function, and branch coverage. Cover success, rejection, boundary, and adversarial paths with unit tests, fuzzing, and stateful invariants. Check accounting conservation, permissions, and valid state transitions; add storage-layout checks for upgrades.
- Run focused tests while editing; run the required coverage, fuzz, and invariant suites on the final change with reproducible seeds and the project's run/depth settings. Report uncovered or uninstrumentable paths; do not exclude production code or weaken properties to claim full coverage.
- Run Slither with the project's actual compiler, dependencies, and remappings. Investigate findings, fix confirmed defects, and explain false positives rather than blanket-suppressing warnings. Report unavailable analysis as incomplete.
- Prefer `@0xdoublesharp/abi-typegen` for new bindings; keep a different existing generator unless the task migrates it. After ABI changes, run `forge build`, regenerate and check bindings, and check affected consumers. With abi-typegen, use `abi-typegen generate`, then `abi-typegen generate --check`, matching the consumer's target. Do not hand-edit output. `forge typegen` requires project shell integration.
- Pin fork tests to a chain and block. Missing archive data leaves a check incomplete; it never counts as zero. Any reachable fund-loss, authority takeover, or blocked-recovery path is must-fix regardless of rarity.
- Send transactions, deploy, upgrade, or publish live verification only when authorized. Use the requested audit tooling rather than rebuilding its workflow.
