---
name: "ds-consult"
description: "Use when asking Codex or Claude for an independent opinion, or when the user asks for a model council."
---

# Independent opinions and councils

Use one reviewer from the other provider for a normal consult. For a requested council, follow [the council procedure](references/council.md). Honor the user's providers and models; report unavailable choices without substitutions.

Write a fresh brief: goal, exact repository/files or diff, constraints, completed checks, question, and stop boundary. Omit secrets, unrelated context, and your preferred verdict.

Reviewers inspect only; the coordinator owns edits and checks. Inside T3, use [host delegation](references/t3.md). Elsewhere, use [standalone CLIs](references/standalone.md). A failed route does not authorize a different route or a permission bypass.

Accept only a completed, substantive answer. Timeouts, empty replies, and partial streams leave the consult incomplete. Verify claims against the source before acting. Use one review and one recheck of corrections unless the user requests another process; do not manufacture agreement by adding reviewers or rounds.

Report the recommendation, supporting reasons, and unresolved disagreements. Consulting does not authorize implementation, messages, merges, or deployment.
