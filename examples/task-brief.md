# Task brief example

Task: cli-limit-fix. Repository and head: record the actual path and Git revision.

Requested outcome: --limit accepts 1 through 1000 and rejects zero. Preserve the other flags.

Scope: the parser and its existing test target. The new cache proposal is a follow-up.

Proof: observe the zero regression fail before the fix, then pass with the relevant boundary cases; run the required integration gate once at the end.

Resources: use the project's existing Scratch wrapper and namespace. Record the actual build/tmp/report directories, owner, current consumer, and retirement event.

Remaining work: keep each outcome pending, complete with evidence, or blocked by a specific prerequisite. Continue independent outcomes. Passing parser tests do not qualify an unrelated native GUI or provider flow.

This brief is a working view linked to the project's existing task record. It does not replace an existing source of truth.
