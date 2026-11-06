---
name: "ds-solidity"
description: "Use when changing Solidity contracts, Foundry tests, upgrade layouts, or fork-dependent behavior in an existing contract project."
---

# Solidity contract changes

- Reuse pinned dependencies, Foundry configuration, libraries, and wrappers. Preserve project compiler requirements and keep artifact/cache paths warm and consistent.
- Require 100% production-contract line, statement, function, and branch coverage. Cover success, rejection, boundary, and adversarial paths with unit tests, fuzzing, and stateful invariants. Check accounting conservation, permissions, and valid state transitions; add storage-layout checks for upgrades.
- Run focused tests while editing; run the required coverage, fuzz, and invariant suites on the final change with reproducible seeds and the project's run/depth settings. Report uncovered or uninstrumentable paths; do not exclude production code or weaken properties to claim full coverage.
- Run Slither with the project's actual compiler, dependencies, and remappings. Investigate findings, fix confirmed defects, and explain false positives rather than blanket-suppressing warnings. Report unavailable analysis as incomplete.
- Rebuild ABI artifacts, regenerate affected language bindings, and check generated output and callers against the new ABI.
- Pin fork tests to a chain and block. Missing archive data leaves a check incomplete; it never counts as zero. Any reachable fund-loss, authority takeover, or blocked-recovery path is must-fix regardless of rarity.
- Send transactions, deploy, upgrade, or publish live verification only when authorized. Use the requested audit tooling rather than rebuilding its workflow.
