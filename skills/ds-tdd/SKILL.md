---
name: "ds-tdd"
description: "Use when implementing a testable change to observable program behavior or repairing a regression."
---

# Test first, then fix

1. Read project instructions and contribution guidelines (`CONTRIBUTING*` or `CONTRIBUTOR*`), including in forks and local projects. Follow the project's architecture, style, tooling, and required checks. Add the test beside existing tests at the smallest public boundary that shows the behavior; one test can cover several helpers.
2. Run it and observe the expected failure. Compile errors, missing fixtures, and setup failures don't count. If a regression won't reproduce after two tries, report that and use the best available check.
3. Make the smallest passing change. Run the focused test, then nearby tests for the changed code.

Group related cases in one test target. Use ds-work for broad-check timing. Keep a passing fix; don't revert it to watch the test fail again.

Change a test when its expectation is wrong, and explain why in the handoff. Don't delete or weaken an assertion to get a pass.

For prose, formatting, and generated output without changed runtime behavior, check the artifact directly. Configuration that changes program behavior still needs a behavioral check.
