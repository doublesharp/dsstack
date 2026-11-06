---
name: "ds-review"
description: "Use when reviewing a change, or when coordinating a requested independent review before handoff."
---

# Review for what breaks

Read the finished diff against the ask, project instructions, and contribution guidelines (`CONTRIBUTING*` or `CONTRIBUTOR*`), in forks and local projects alike. Inspect callers and dependencies needed to judge behavior and project conventions. Skip unrelated code and personal style preferences.

- **Must fix:** breaks the ask or explicit project requirements, regresses behavior, or opens a security, data-loss, or fund-loss path. Rarity doesn't lower the severity.
- **Follow-up:** improvements outside that boundary. List them in the handoff and leave them out of this change.

Each finding needs a location, triggering scenario, impact, and suggested fix. Confirm it against the code before acting; mark it fixed, disputed with a reason, or follow-up.

Use an independent reviewer when requested, required by the project, or when changes move funds or affect authentication. Give the ask, diff, and completed checks without hinting at a verdict. Reviewers start no other reviewers. For Codex/Claude cross-review, use ds-consult.

Review once, then recheck must-fix corrections once. Fix a new must-fix inside a correction and mention it in the handoff; don't start another review round unless requested.
