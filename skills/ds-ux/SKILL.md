---
name: "ds-ux"
description: "Use when asked for a measured UX/design hill climb with alternating Codex/Claude implementation and council scoring, or its seven-category evaluator role. Routine interface edits use ds-web."
---

# Improve against the previous best

## Frame the comparison

- Infer the app, users, journey, and role; state assumptions and scope. An evaluator inspects only. Delegated implementers/evaluators perform only their assigned role and start no agents; evaluators use the rubric directly.
- State the target and budget using [ds-work targets](../ds-work/references/targets.md). Use [ds-web](../ds-web/SKILL.md) for browser checks, [the rubric](references/rubric.md) for 0–10 category scores, and [the council procedure](references/council.md) for model handoffs and scoring. Keep product identity, essential content, and functionality intact; a new style alone is not an improvement.
- Verify the preview serves the intended checkout and journey using existing seeds or fixtures; report missing journey data before expanding setup. Keep live-site, local-fixture, and error-page findings separate. Environment repair follows ds-work's attempt limit.

## Establish the baseline

- Inspect actual screenshots and exercise the journey. Capture 390×844, 768×1024, and 1440×900 CSS viewports; check 360px width and real desktop 200% zoom as stress cases. Verify actual viewport dimensions. A smaller viewport or CSS zoom is not browser zoom.
- Match browser, zoom, theme, display scale, route, data, scroll, state, loaded fonts, and settled animations between versions. Label captures by version/device/page/state and keep them in the project's disposable-output location.
- Exercise applicable journey states and touch, pointer, keyboard, and focus behavior. Mark inaccessible coverage “Not evaluated.” Have the council score the baseline and rank three priorities, each with a screenshot reference, task impact, and observable acceptance criterion.

## Improve and evaluate

- Alternate implementation: Codex in odd rounds, Claude in even rounds, unless the user chooses the starting provider. Keep one writer at a time. Use host delegation for implementation handoffs and [ds-consult](../ds-consult/SKILL.md) for read-only council scoring. Use the requested models; report unavailable providers rather than substituting a solo pass.
- Give each implementer the retained best, latest council feedback, next priority, and remaining rounds. Implement one coherent priority, stating the expected user benefit and affected categories. Preserve a recoverable previous best without overwriting unrelated edits. Use ds-tdd for behavior changes and ds-work for check timing.
- Submit matched previous-best and candidate screenshots, scope/gaps, diff, and check results to fresh Codex and Claude evaluators. Neither is the implementation agent. Each independently scores both versions and recommends ACCEPT or REVISE; the coordinator applies the acceptance rule. Do not self-award acceptance.
- ACCEPT requires a higher unrounded council aggregate, no category/device regression in either evaluator's matrix, both ACCEPT recommendations, passing fast covering checks, and an intact journey and essential content. Missing scoring-device, journey, or covering-check evidence leaves the decision pending. Unavailable stress checks are reported gaps unless required for acceptance by the ask. A regression means REVISE; request a decision only if deliberately pursuing that specific tradeoff.
- Start the next round from the accepted best using the council's highest-impact feedback. A tie or rejection keeps the best unchanged; revise or replace the candidate, never resubmit it unchanged. At finish, restore only your unaccepted changes, including pending candidates, without disturbing unrelated edits.

After the baseline and each verdict, show the seven-category scorecard and update one compact progress table: round, implementer, council device totals/aggregate, paired delta, lowest category/device, decision, and accepted best. Keep pending and rejected scores distinct from accepted progress. End with the retained version, observed task gains, checks, gaps, and stop reason.
