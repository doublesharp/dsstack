---
name: "ds-tdd"
description: "Use when implementing a testable change to observable program behavior or repairing a regression."
---

# Behavioral TDD

Before changing behavior, test the smallest useful public or integration boundary. One scenario may cover several helpers. Distinguish the fault from correct behavior; avoid assertions that merely repeat implementation. Validate formatting, documentation, generated metadata, and mechanical edits directly.

1. **Prepare.** Reuse the project runner and representative fixtures. Confirm copied source, dependencies, and mocks reach the claimed behavior. A model or mock cannot qualify an unexercised database, browser, native runtime, or provider.
2. **Observe RED.** Run against unfixed behavior and inspect the expected failing assertion or observable fault. Compile, command, fixture, setup, and unrelated failures are prerequisites to repair, not RED. Record the command and decisive result; report an unreproduced fault honestly.
3. **Make GREEN.** Implement the smallest coherent correction, rerun the focused check, and inspect its assertions and output. Refactor only when useful, keeping regression coverage.

For Rust, batch related cases in one crate/test target using project wrappers and warm Scratch artifacts. Establish a valid fail-to-pass observation, then retain proven code rather than repeatedly reverting it for related cases. Independent faults may need their own reproductions.

Broaden checks for changed dependencies, contracts, or runtime boundaries. Preserve mandatory integration, native, security, and release gates where applicable; a workspace matrix is not an automatic inner-loop step. Report what each check proves and what remains untested.
