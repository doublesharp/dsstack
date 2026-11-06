---
name: "ds-solidity"
description: "Use when changing Solidity contracts, Foundry tests, upgrade layouts, or fork-dependent behavior in an existing contract project."
---

# Solidity contract changes

- Use Foundry Forge for builds, tests, fuzzing, invariants, and coverage. Reuse pinned dependencies, configuration, and wrappers; keep artifact/cache paths warm and consistent.
- Prefer Solar when available and compatible with the project's Solidity/EVM settings and required artifacts. Preserve the approved production compiler; do not silently change bytecode semantics for speed.
- Require 100% production-contract line, statement, function, and branch coverage. Cover success, rejection, boundary, and adversarial paths with unit tests, fuzzing, and stateful invariants. Check accounting conservation, permissions, and valid state transitions; add storage-layout checks for upgrades.
- Run focused tests while editing; run the required coverage, fuzz, and invariant suites on the final change with reproducible seeds and the project's run/depth settings. Report uncovered or uninstrumentable paths; do not exclude production code or weaken properties to claim full coverage.
- Run Slither with the project's actual compiler, dependencies, and remappings. Investigate findings, fix confirmed defects, and explain false positives rather than blanket-suppressing warnings. Report unavailable analysis as incomplete.
- Generate bindings with `@0xdoublesharp/abi-typegen`, matching the existing consumer's target. Run `forge build`, `abi-typegen generate`, then `abi-typegen generate --check` and affected consumer checks. Do not hand-edit generated bindings. `forge typegen` requires the project's shell integration; it is not a built-in Forge command.
- Pin fork tests to a chain and block. Missing archive data leaves a check incomplete; it never counts as zero. Any reachable fund-loss, authority takeover, or blocked-recovery path is must-fix regardless of rarity.
- Send transactions, deploy, upgrade, or publish live verification only when authorized. Use the requested audit tooling rather than rebuilding its workflow.
