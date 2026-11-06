---
name: "ds-tdd"
description: "Use when implementing a testable change to observable program behavior or repairing a regression."
---

# Test the behavior, then fix it

1. Read project instructions and contribution guidelines. Find the smallest existing test boundary that exposes the intended behavior; keep the test with its neighbors.
2. Run it before changing production code. Observe the expected failure; compile errors and broken fixtures do not count. If a regression will not reproduce after two attempts, report that and use the closest useful check.
3. Make the smallest passing change, rerun the focused test, then nearby tests. Run broader required checks after the last edit they cover.

If a useful test would require unrelated infrastructure or mostly verify mocks or implementation details, explain the missing capability and use the closest executable regression check. This does not waive project-required tests. Keep the gap visible in the handoff.

Keep a passing fix; do not revert it just to show the failure again. Change an assertion when its expectation is wrong or the requested contract changes, and explain why. Do not weaken it to make incorrect behavior pass.

Check prose, formatting, and generated output directly. Configuration that changes runtime behavior still needs a behavioral check.
