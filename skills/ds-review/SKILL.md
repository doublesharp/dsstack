---
name: "ds-review"
description: "Use when reviewing a scoped change or coordinating requested independent code review before handoff."
---

# Bounded review

Establish requested outcomes, exact checkout/diff, relevant contracts, and proof limits. Review correctness and material risk. Broaden only for a concrete affected behavior and failure path; optional improvements and style do not block delivery.

Use one independent reviewer when requested, project-required, or justified by security, financial, recovery, or concurrency risk. Supply scope and raw evidence without seeding a verdict. Reviewers cannot launch reviewers. Follow the active harness protocol; use [ds-consult](../ds-consult/SKILL.md) for reciprocal Codex/Claude review or an explicitly requested council. Disclose unavailable models without substitution.

Default to **three rounds total**: initial review plus at most two scoped re-reviews of material fixes and open findings. Nits and resolved findings do not restart review. At the cap, report unresolved issues honestly; the cap grants no acceptance. Explicit user direction may change the budget.

Findings need severity, location, triggering scenario, impact, evidence, and a minimal correction when clear. Rank by impact, reachability, and protections; rarity alone does not downgrade security, authority, financial, recovery, or concurrency failures.

The implementer verifies findings and records fixed, accepted-with-rationale, disproved, or unresolved dispositions. Recheck material edits and preserve mandatory gates. End with a verdict, actual evidence, and exact blockers; source acceptance does not qualify runtime or release.
