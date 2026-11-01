---
name: "ds-consult"
description: "Use when asking Codex or Claude for an independent opinion, or when the user asks for a model council."
---

# Cross-model consult

Codex can consult Claude, and Claude can consult Codex. Default to one reviewer from the other provider. Use the model the user named. If it isn't available, say so instead of substituting another.

Write a fresh brief with the goal, the repository path and exact files or diff, constraints, what you've already run, the question, and when to stop. Leave out secrets and unrelated material.

Consults are read-only. You keep the decisions, the edits, and the checks. Inside T3, follow [T3 delegation](references/t3.md). Elsewhere, use [the standalone CLIs](references/standalone.md). If a route fails, report it. A failed route is not permission to get around harness policy another way.

Hold a council only when the user asks for one. Use their roster, or one Codex and one Claude reviewer. Reviewers work independently on the same material, with no nested reviews and no agreement loop. The ds-review round limit covers the whole council unless the user sets another.

A consult counts only when it completes with a substantive answer. Partial output, timeouts, and empty replies don't count. Check each claim against the code before acting on it, and keep working on other items while you wait.
