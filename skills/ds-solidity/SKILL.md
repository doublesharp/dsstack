---
name: "ds-solidity"
description: "Use when changing Solidity contracts, Foundry tests, upgrade layouts, or fork-dependent behavior in an existing contract project."
---

# Solidity contract changes

Use the repository's compiler, Foundry configuration, libraries, wrappers, and deployment conventions. Identify the changed invariant, caller permissions, and affected state before editing. Preserve existing compiler and dependency pins.

Begin behavioral changes with a focused Foundry test that fails for the expected contract behavior. Compilation failure or a broken fork fixture does not qualify as RED. Cover the meaningful authorized and rejected paths, then rerun the same target after implementation. Route outputs and caches through the project's Scratch configuration, propagating those locations into downstream Forge invocations.

Choose broader gates from the change's risk. Accounting, state-machine, and adversarial interaction changes can warrant fuzz or invariant tests. Upgrade changes require the project's storage-layout and upgrade checks. Run coverage when required or when it resolves a concrete reachability question. Avoid rerunning every expensive gate after each local assertion change.

Fork evidence needs an explicit chain, block number or hash, source identity, and suitable historical RPC. Keep pinned historical calls pinned. An unavailable archive or an incomplete response is an unresolved proof, not a successful zero. Tests against mocks, forked state, and live contracts support different claims.

Assess security severity by plausible impact and exploit conditions. A rare path that can lose funds, seize authority, or prevent recovery remains serious. For an explicitly requested audit or harness effort, use available user-selected tooling, such as Pashov for an audit or fizz for fuzz harness work; do not reproduce those workflows here.

Passing tests does not authorize moving funds, upgrading, deploying, or publishing verification. Report the tested source and remaining live operation gates explicitly.
