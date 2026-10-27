---
name: "ds-solidity"
description: "Use when changing Solidity contracts, Foundry tests, upgrade layouts, or fork-dependent behavior in an existing contract project."
---

# Solidity contract changes

Use pinned compiler/dependencies, Foundry configuration, libraries, wrappers, and deployment conventions. Identify changed invariants, caller permissions, and affected state.

Start with a focused failing behavioral Foundry test; compile failures or broken fork fixtures do not qualify as RED. Cover meaningful authorized/rejected paths, implement, and rerun the target. Route outputs/caches to Scratch and propagate those paths into downstream Forge invocations.

Choose broader gates by risk: accounting, state-machine, and adversarial interactions may warrant fuzz/invariant tests; upgrades require storage-layout/upgrade checks. Run coverage when required or resolving concrete reachability questions. Avoid repeating expensive gates after each assertion edit.

Fork evidence needs explicit chain, block number/hash, source identity, and suitable historical RPC. Preserve historical pins; unavailable archives or incomplete responses leave proof unresolved, never a successful zero. Distinguish mocks, forks, and live contracts.

Assess severity by plausible impact and exploit conditions: rare paths that lose funds, seize authority, or prevent recovery remain serious. For explicitly requested audits/harnesses, use available user-selected tooling, such as Pashov or fizz, without duplicating their workflows.

Tests grant no authority to move funds, upgrade, deploy, or publish verification. Report tested source and remaining live-operation gates.
