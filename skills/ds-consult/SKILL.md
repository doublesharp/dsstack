---
name: "ds-consult"
description: "Use for independent model reviews of substantial changes or consequential decisions, or when the user asks for a second opinion or model council."
---

# Independent opinions and councils

For a substantial change or consequential decision, make your own assessment and prefer a [council](references/council.md) with one reviewer from each of the other two providers among Codex, Claude, and Gemini. If you work outside that roster, prefer one reviewer from each. Handle small, well-understood tasks directly. For a focused second opinion, choose one reviewer from another provider.

Honor the user's roster and model choices. Choose available models and reasoning effort for the task's domain, complexity, and tool needs. Use a smaller panel when the question or budget warrants it. Report unavailable reviewers without substituting providers. If a default reviewer is unavailable, continue with the available reviews.

Write a fresh brief: goal, exact repository/files or diff, constraints, completed checks, question, and stop boundary. Omit secrets, unrelated context, and your preferred verdict.

Tell reviewers to inspect only and start no nested agents. Inside T3, use [host delegation](references/t3.md). Elsewhere, use [standalone CLIs](references/standalone.md). A failed route does not authorize a different route or a permission bypass.

Count only completed, substantive answers. Verify claims against the source before acting. Use one review round and at most one recheck of corrections unless the user requests another process.

Report the recommendation, supporting reasons, and unresolved disagreements. Consulting does not authorize implementation, messages, merges, or deployment.
