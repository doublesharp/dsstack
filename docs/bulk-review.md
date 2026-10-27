# Planning and bulk review

Reviewed 2026-10-27 after adding `ds-spec` and `ds-plan`.

**Verdict: keep the 15 skills.** One independent read-only pass found no justified whole-skill deletion or mandatory workflow chain. Spec discovery, implementation planning, delivery tracking, and final handoff have distinct uses. Existing specs, project trackers, and authorization carry forward.

## Size

| Measure | Words |
|---|---:|
| All 15 entrypoints, including metadata | 3,226 |
| Longest entrypoint | 238 |
| All entrypoint bodies | 2,907 |
| All discovery descriptions | 244 |
| Conditional consultation references | 444 |
| Original 12 entrypoints before shortening (`29764fa`) | 3,651 |

Entrypoints are about 12% shorter than the original twelve combined. Including conditional references gives 3,670 words, roughly the original total. These are whitespace counts, not measured tokens, latency, or agent effectiveness. Names and descriptions are exposed at discovery; selected bodies and relevant references are loaded as needed.

## Corrections applied

- `ds-plan` now selects behavioral tests for behavior changes and direct artifact checks for mechanical work, avoiding invented tests per task.
- `ds-web` now limits visual checks to affected states, avoiding a layout/breakpoint sweep for a color edit.
- `ds-work` is narrowly described as delivery tracking/resumption, separating it from plan authoring. Its brief outcome reconciliation remains useful alongside the more complete `ds-finish` handoff rules.

Domain TDD reminders remain because each skill should work independently; removing them would encourage mandatory cross-skill loading. No automatic router, reviewer panel, recurring review, or additional approval gate was added.

## Request-path check

- A clear color edit proceeds directly with relevant authorized verification, without a spec or implementation plan.
- An unclear paid-membership feature first resolves consequential product and financial/access questions; execution planning follows when dependencies require it.
- An adequate supplied spec with permission to implement is reused; only missing execution decisions are planned, without reopening approval.

This was one static review with proposed action paths, not executed application journeys. Revisit consolidation only if real tasks show repeated loading, misrouting, or process that delays requested outcomes.
