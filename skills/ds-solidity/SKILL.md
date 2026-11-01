---
name: "ds-solidity"
description: "Use when changing Solidity contracts, Foundry tests, upgrade layouts, or fork-dependent behavior in an existing contract project."
---

# Solidity contract changes

- Use the pinned compiler, dependencies, Foundry config, libraries, and wrappers. Route `out/` and caches to Scratch, and pass the same paths to every `forge` command.
- Start with a failing Foundry test of the behavior that covers allowed and rejected callers. Compile errors and broken fork fixtures don't count as that failure.
- Add fuzz or invariant tests for accounting and state-machine changes, and storage-layout checks for upgrades. Run coverage only when asked or to settle a specific reachability question.
- Pin fork tests to a chain and block number. A missing archive node or an incomplete RPC response leaves the result unknown. It never counts as zero.
- Treat any path that loses funds, takes over authority, or blocks recovery as must-fix, however rare.
- Run expensive suites, such as long fuzz campaigns, invariants, and coverage, once at the end rather than after each assertion change.
- Don't send transactions, deploy, upgrade, or publish verification on a live network unless the user tells you to.
- For a requested audit, use the tooling the user picked, such as Pashov or fizz, without re-creating its workflow.
