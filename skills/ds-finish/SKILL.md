---
name: "ds-finish"
description: "Use when preparing a handoff for a requested change after its applicable verification and review."
---

# Request-complete handoff

Reconcile the requested outcomes with the actual diff and acceptance evidence. Verify the named checkout and current changes. Remove accidental scope expansion and unfinished scaffolding. Preserve unrelated user work and other workers' files.

Run the checks required for the changed behavior and the current integration boundary, then read their results. Reuse fresh applicable evidence; rerun after a material change or when an earlier result no longer covers the final state. Do not repeatedly broaden testing after relevant checks pass without a concrete concern. Required integration and release gates remain mandatory when applicable.

Resolve actionable review findings or record an evidence-backed disposition. Keep source, fixture, artifact, browser, database, native/runtime, provider, financial, deployment, and production evidence distinct. An unavailable required check is an open gate, not a passing result. If a necessary outcome remains blocked, describe the partial result and exact dependency rather than declaring completion.

Clean only task-owned disposable output whose ownership and open processes have been checked. Preserve shared caches and active work. Keep bulky evidence on Scratch and leave only short maintained summaries in the repository.

The handoff states what changed and why, what was actually verified, material limitations, and any remaining gate with its owner. **Finished means the authorized request is complete and ready for human review.** This skill grants no merge, push, deployment, external-message, or data-deletion authority. Follow existing authorization and harness policy for those actions; do not add a ceremonial approval checkpoint to already-authorized work.
