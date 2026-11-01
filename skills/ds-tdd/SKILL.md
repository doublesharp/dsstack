---
name: "ds-tdd"
description: "Use when implementing a testable change to observable program behavior or repairing a regression."
---

# Test first, then fix

1. Write the test at the smallest public boundary that shows the behavior, such as a public function, a CLI command, an HTTP route, or a component. One test can cover several helpers. Put it with the existing tests.
2. Run it and watch it fail for the reason you expect. Compile errors, missing fixtures, and setup failures don't count, so fix those first. If the bug won't reproduce after two tries, say so and fix it with the best check you have.
3. Make the smallest change that passes. Rerun that test, then the nearby tests for the code you touched.

Group related cases in one test target and run them together. Keep the inner loop on that target and leave broad suites for the end, as ds-work describes. Once a fix passes, keep it. Don't revert it to watch the test fail again.

Change a test only when the test itself is wrong, and say so in the handoff. Never delete or weaken an assertion to get a pass.

Docs, formatting, config, and generated files don't need new tests. Check them directly by rendering, parsing, or diffing them.
