---
name: "ds-review"
description: "Use when reviewing a change, or when coordinating a requested independent review before handoff."
---

# Review for what breaks

Read the full target diff (including staged and untracked files for a working tree) against the ask, project instructions, and contribution guidelines. Inspect the callers and dependencies needed to judge behavior. Skip unrelated code and personal style preferences.

- **Must fix:** a demonstrated violation of the ask or project requirements, regression, or security, data-loss, or fund-loss path. Rarity does not lower severity.
- **Follow-up:** improvements outside that boundary.

For each finding, give its location, triggering input, impact, and suggested fix. Use a focused reproduction when practical; otherwise trace the complete code path from input to failure, including its preconditions. Keep unverified concerns separate from confirmed defects. Mark findings fixed, disputed with a reason, or follow-up.

When fixes are requested, search the changed code once for the same root cause and reuse reproductions as regression checks. Do not expand that search into unrelated cleanup.

Use independent reviewers when requested or required by the project. For substantial changes, prefer a cross-provider council and use `ds-consult` when available. Give the ask, diff, and completed checks without suggesting a verdict. Honor the requested providers and report unavailability. Reviewers inspect only and start no nested reviews.

Review once and recheck must-fix corrections once. Fix any new defect inside a correction without another review round unless requested. Finish with findings and remaining gaps; a review alone does not authorize edits or release.
