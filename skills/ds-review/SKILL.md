---
name: "ds-review"
description: "Use when reviewing a change, or when coordinating a requested independent review before handoff."
---

# Review for what breaks

Review the diff against the ask, reading the callers and dependencies you need to judge the changed behavior. Skip style and unrelated code. Sort each finding into one of two groups.

- Must fix. It breaks the ask, regresses existing behavior, or opens a security, data-loss, or fund-loss path. Rarity doesn't lower it.
- Follow-up. Everything else. List these in the handoff and leave them out of this change.

For each finding, give the location, the scenario that triggers it, the impact, and a suggested fix.

Bring in an independent reviewer only when the user asks, the project requires it, or the change moves funds or touches authentication. Review the finished diff once, not each step. Give the reviewer the ask, the diff, and what you ran, without hinting at a verdict. Reviewers don't start other reviewers. For a Codex and Claude cross-review, use ds-consult.

Run one review, then one re-check of the must-fix fixes, and stop. If the re-check finds a new must-fix inside a fix, fix it and note it in the handoff rather than opening another round, unless the user asks for more.

Confirm each finding against the code before acting on it, because reviewers are sometimes wrong. Mark each one fixed, disputed with a reason, or follow-up.
