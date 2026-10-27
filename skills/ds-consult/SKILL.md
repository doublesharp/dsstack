---
name: "ds-consult"
description: "Use when requesting independent feedback from Codex or Claude/Opus, or when the user asks for a model council."
---

# Cross-model consultation

Codex can consult Claude; Claude can consult Codex. Default to one opposite-provider reviewer. Preserve a named model/version and requested settings; discover availability rather than guessing identifiers or silently substituting.

Prepare a fresh brief: goal, repository and exact files/diff or hashes, constraints, prior checks with proof limits, concrete question, and stopping condition. Include only relevant authorized development code; exclude secrets and unrelated material. Existing sharing authorization applies without repeated visibility/consent checks.

Default to read-only review with available tool restrictions. The lead owns decisions, edits, verification, and handoff. Peer edits require explicit implementation authority and appropriate isolation; consultation grants no external-action permission.

Use [T3 delegation](references/t3.md) inside T3. Outside it, use [standalone CLIs](references/standalone.md). Follow current harness policy; a failed T3 route is not permission to bypass it through a CLI.

For an explicitly requested **council**, honor the requested roster; otherwise use one Codex and one Claude reviewer. Give independent reviewers the same evidence and distinct relevant questions. No nested reviews or agreement loop. Apply [ds-review](../ds-review/SKILL.md)'s round budget across the council, not per member.

Require successful completion and a substantive final result; partial output, timeout, interruption, and empty responses are incomplete. Deduplicate findings, verify material claims, record disagreements/dispositions, and continue independent requested work. Label tool-less feedback as evidence-packet synthesis; it cannot establish repository or runtime verification.
