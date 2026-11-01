# Task brief example

Task: cli-limit-fix in `<repo>` at `<sha>`.

Ask: `--limit` accepts 1 through 1000 and rejects 0. Other flags don't change.

Items:

1. Reject zero. Done when the new zero case fails before the fix and passes after it, along with the existing parser tests.
2. Final check. Done when the project's required check passes once on the final diff.

Follow-ups, not in this change: the cache proposal.

Blockers: none.

Keep this next to the project's own task record instead of replacing it.
