---
name: "ds-tdd"
description: "Use when implementing a testable change to observable program behavior or repairing a regression."
---

# Behavioral TDD

Choose the smallest meaningful test of the requested behavior before changing production code. Exercise a useful public or integration boundary; one scenario can cover several helpers. Tests should distinguish correct behavior from the reported fault, rather than repeat implementation details. For formatting, documentation, generated metadata, and other mechanical changes, use artifact validation instead of inventing behavioral tests.

1. **Establish the test.** Reuse the project's runner and representative fixture. Check that copied source, dependency setup, and mocks actually reach the behavior being claimed. Preserve the relevant runtime boundary; a model or mock does not prove a database, browser, provider, or native runtime.
2. **Observe RED.** Run the focused command against the unfixed behavior and read the failure. A valid RED is an assertion or observable failure caused by the missing behavior. Compile errors, missing commands, bad fixtures, setup failures, and unrelated failures do not qualify. Repair those prerequisites, then observe behavioral failure. Record the command and decisive output. If the fault cannot be reproduced, report that limit rather than inventing RED.
3. **Make it pass.** Change production code to satisfy the behavior, then rerun the relevant command. Inspect the actual assertions and output before calling it GREEN. Refactor only when useful, retaining the behavior check.

For Rust, select one crate and one test target for the inner loop; batch related regression cases there before compiling. Use the project wrapper and its Scratch target directory. Obtain at least one valid fail-to-pass observation for the behavior being fixed. Once that observation is established, keep the proven code: do not repeatedly revert it to demonstrate RED for each related case. A new independent fault may need its own reproduction, not another full build cycle by ritual.

Run additional checks when a concrete dependency, changed contract, or integration boundary justifies them. Whole-workspace builds are not an automatic inner-loop step. Mandatory broader integration, native, security, and release gates still apply at their proper boundaries. Report separately what each kind of evidence proves and what remains untested.

Inspiration: Superpowers' test-driven-development practice, adapted for behavioral evidence and bounded build cost.
