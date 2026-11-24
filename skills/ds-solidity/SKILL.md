---
name: "ds-solidity"
description: "Use when changing Solidity contracts, Foundry tests, upgrade layouts, or fork-dependent behavior in an existing contract project."
---

# Solidity contract changes

- Use `forgeds` through project wrappers (including nested `forge` calls) with `--use solar` for compatible local and CI development checks, keeping the approved compiler for deployed bytecode, required coverage, and release artifacts. Preserve consumer artifact paths and warm compiler caches; read [the forgeds toolchain guide](references/forgeds.md) for installation, shared compiler caching, `compiler_warnings = "changed"`, and `--instrumented` coverage iteration.
- Require 100% production-contract line, statement, function, and branch coverage. Check success, rejection, boundaries, adversarial paths, accounting, permissions, state transitions, and upgrade storage layouts. Run focused tests while editing, then required coverage, fuzzing, and stateful invariants with reproducible seeds and project run/depth settings. Report uncovered or uninstrumentable paths; do not exclude production code or weaken properties to claim full coverage.
- Run Slither with the project's actual compiler, dependencies, and remappings. Investigate findings, fix confirmed defects, and explain false positives rather than blanket-suppressing warnings. Report unavailable analysis as incomplete.
- Prefer `@0xdoublesharp/abi-typegen` for new bindings; keep a different existing generator unless the task migrates it. After ABI changes, rebuild, regenerate and check bindings, and check affected consumers. With abi-typegen, use `abi-typegen generate`, then `abi-typegen generate --check`, matching the consumer's target. Do not hand-edit output. Typegen subcommands require project shell integration.
- Pin fork tests to a chain and block. Missing archive data leaves a check incomplete; it never counts as zero. Any reachable fund-loss, authority takeover, or blocked-recovery path is must-fix regardless of rarity.
- Use the requested audit tooling rather than rebuilding its workflow.
