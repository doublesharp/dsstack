---
name: "ds-review"
description: "Use when reviewing a scoped change or coordinating requested independent code review before handoff."
---

# Bounded, evidence-based review

Identify the requested outcomes, exact checkout or diff, relevant contracts, and available verification. Review correctness and material risk within that scope. Broaden only for a concrete interaction, explaining the affected behavior and failure path. Optional improvements and style preferences do not become blockers.

Use one independent reviewer when independent review is requested or materially useful. Give that reviewer the scope, raw artifacts, and proof limits; do not seed a desired verdict. Reviewers must not launch nested reviewers. Follow T3's tool and harness protocol. If the requested model is unavailable, disclose the limitation and available path instead of silently substituting one.

Default to **three review rounds total**: the initial review and at most two scoped re-reviews. Count the initial review as round one. A re-review checks material fixes and their affected interactions; it does not restart the whole review. Nits, wording, and already-resolved findings do not create another round. At the cap, report unresolved evidence and decisions honestly instead of cycling until a reviewer is silent. Explicit user direction can change the budget.

For each actionable finding, state severity, file/location, triggering scenario, impact, and supporting evidence; suggest the smallest correction when clear. Rank by impact, reachability, and existing protections. Rare security, authorization, financial, recovery, or concurrency failures can remain severe: low frequency alone is not a downgrade.

The implementer verifies each finding and may disagree with source, contract, or runtime evidence. Record the disposition: fixed, accepted with rationale, disproved, or unresolved. Agreement is not a substitute for correctness. Re-run checks relevant to material edits and preserve mandatory integration gates. Finish with a clear verdict, concise evidence, and any exact remaining blocker; distinguish source acceptance from runtime or release qualification.
