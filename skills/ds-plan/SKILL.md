---
name: "ds-plan"
description: "Use when turning an adequate spec or clear requirements into implementation tasks with meaningful dependencies or handoffs."
---

# Executable implementation plan

Read the spec, existing plan, project instructions, and affected code. Clear small fixes need no separate plan. Reuse adequate requirements; resolve material gaps rather than inventing decisions or forcing a new spec.

Decompose by independently deliverable behavior, not every file or coding action. For each task record:

- Requirement and checkable result; owner/dependencies when shared.
- Affected files and responsibility, plus exact interfaces or values already decided.
- Focused verification and command: behavioral tests for behavior changes, direct artifact checks for mechanical edits, and decisive evidence.
- Required integration, native, provider, or release gates at the appropriate boundary.

Keep related setup, docs, and tests with their deliverable. Preserve project-wide constraints and consistent cross-task types/names. Sketch only algorithms or contracts needing explanation; do not prewrite routine code or speculative signatures.

Budget expensive checks. Batch related Rust cases in existing targets, reuse warm worktree artifacts, and place broader required checks at integration rather than after every step. A task may contain one coherent RED/GREEN cycle; each checkbox needs no separate build or reviewer.

Self-check requirement coverage, interfaces, command validity, and proportion. Save in the project's existing docs/task system and link its spec. Follow the authorized execution method without reopening approval or choosing a new tracker. A planning-only request ends at the reviewable plan.
