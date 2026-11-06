---
name: "ds-solidity"
description: "Use when changing Solidity contracts, Foundry tests, upgrade layouts, or fork-dependent behavior in an existing contract project."
---

# Solidity contract changes

- Use the pinned compiler, dependencies, Foundry config, libraries, and wrappers. Keep configured `out/` and cache paths consistent across `forge` commands.
- Cover allowed and rejected callers in behavioral tests. Add fuzz or invariant tests for accounting and state-machine changes, and storage-layout checks for upgrades. Run coverage when requested or to settle a reachability question.
- Pin fork tests to a chain and block. A missing archive node or incomplete RPC response leaves the result unknown; it never counts as zero.
- Treat any path that loses funds, takes over authority, or blocks recovery as must-fix, however rare.
- Send transactions, deploy, upgrade, or publish live-network verification only when the user authorizes it.
- For a requested audit, use the user's chosen tooling rather than re-creating its workflow.
