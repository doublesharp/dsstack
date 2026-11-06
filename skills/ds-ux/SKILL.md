---
name: "ds-ux"
description: "Use when asked for a measured UX/design hill climb with alternating Codex/Claude implementation and council scoring, or its seven-category evaluator role. Routine interface edits use ds-web."
---

# Improve against the previous best

Use this workflow for a requested measured UX improvement. An evaluator-only task ends after scoring. Keep product identity, essential content, and working journeys intact.

## Establish the baseline

- Identify users, primary journey, supplied references, and the requested target. Read [targets and rounds](references/targets.md), [the rubric](references/rubric.md), and [paired scoring](references/scoring.md).
- Reuse the project's running app, login, seeds, and browser tools. Verify the checkout and journey before scoring. Follow the repair limit in the round budget.
- Capture 390×844, 768×1024, and 1440×900 CSS viewports. Check 360px width and actual browser 200% zoom as stress cases; a resized viewport is not zoom. Use matched capture conditions and the project's disposable-output location.
- Exercise relevant initial, loading, empty, error, success, navigation, and keyboard/focus states in supported themes. Inspect [branding and sharing details](references/finishing.md), including logos, favicons, and Open Graph previews. Mark inaccessible coverage unevaluated.

## Improve and score

- Alternate Codex and Claude implementers unless the user chooses another order. Keep one writer at a time. Report unavailable requested providers without substituting a solo run.
- Give each writer the retained best, last feedback, one priority, and remaining rounds. Consider a coherent custom icon set when existing iconography weakens clarity or visual identity; use the project's SVG/icon pipeline. Preserve a recoverable previous best and unrelated edits.
- Use fresh independent Codex and Claude evaluators for each pair. Give both the same scope, matched captures, rubric, diff, and checks. Hide desired scores, implementer identity, and the other judge's answer.
- Apply the [paired scoring acceptance rule](references/scoring.md#acceptance); missing evidence leaves the decision pending.
- A rejection keeps the best unchanged. Try a different candidate within the remaining budget; do not resubmit unchanged work. At finish, restore only your unaccepted changes.

Test changed behavior at its smallest existing boundary. Run fast covering checks per candidate and slow required checks once on the final retained version. A failed required check blocks completion. Show the scorecard after baseline and each verdict; hand off the retained version, observed gains, checks, gaps, and stop reason.
