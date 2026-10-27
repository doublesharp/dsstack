---
name: "ds-spec"
description: "Use when shaping unclear feature requirements or consequential design decisions into a buildable specification."
---

# Buildable specification

Read existing behavior, project instructions, supplied context, and prior decisions before asking questions. Clear small changes can proceed directly; reuse an adequate spec instead of rewriting it.

Identify intent, users, goals, non-goals, constraints, and observable success. Clarify only unknowns that materially change behavior, scope, cost, or authority and cannot be resolved locally. Distinguish user decisions from assumptions and recommendations; honor delegated choices.

For consequential design choices, compare viable approaches and tradeoffs, recommend one, and record the decision. Investigate or spike only to answer a named uncertainty within existing authorization; label throwaway results.

Write enough for another implementer to build: behavior and important failure cases, component/data/interface boundaries, relevant permissions and recovery, acceptance criteria, constraints, and unresolved decisions. Include exact values the user requires; leave routine implementation choices open.

Use a short note for bounded work and a durable spec for larger work, in the project's existing docs or task system. Link existing evidence instead of duplicating it. Resolve material ambiguity before dependent implementation, continuing independent work where possible.

Respect plan-only requests and existing review gates. Explicit authorization to proceed carries forward; writing a spec creates no new approval ceremony. A necessary implementation plan records execution decisions separately.
