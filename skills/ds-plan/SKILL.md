---
name: "ds-plan"
description: "Use when the user asks for a spec or plan, or when a feature request is unclear enough that building the wrong thing is the main risk."
---

# Plan only as much as the work needs

Small, clear tasks need no separate plan.

1. Read relevant code, docs, and existing plans. Reuse what fits.
2. Ask only for missing information that changes what gets built and isn't available in the repo. State a reasonable assumption for routine choices.
3. For choices expensive to reverse, give two or three options with trade-offs and a recommendation.
4. Describe the behavior, important failure cases, interfaces and data dependencies, and scope boundaries. Leave routine implementation details to the implementer.
5. Order deliverables by dependency. Name files and observable completion checks; identify independent items when parallel work helps. Schedule slow checks once, after the edits they cover.

Size the plan to the task: a few lines for a small feature, a document for multi-week work. Save durable plans with project specs or its tracker. A plan-only request ends with the plan; an implementation request continues into the work.
