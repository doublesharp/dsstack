# Alternating implementers, independent scoring

Use one Codex and one Claude evaluator for the baseline and every candidate. Keep the same requested model pair and rubric throughout. Evaluators are fresh agents, separate from the current implementation agent, even when they share its provider. They inspect only and start no nested agents. An evaluator-only request ends after evaluation without implementation rounds.

Implementation alternates Codex → Claude → Codex → Claude, or starts with Claude when requested. This is a serial handoff: the previous writer stops before the next starts. The coordinator sends the retained version, latest matrices and feedback, chosen priority, scope/data/capture conditions, gaps, check results, round number, and no-progress count. Do not make the next implementer rediscover the baseline.

Send both evaluators the same matched screenshots, running interface, rubric, diff, and check results, plus each evaluator's own provider's previous matrix for the retained best, never the other provider's. Ask them to inspect the rendered images and affected journey, explain every changed score, and return both matrices, aggregates, priorities, and a verdict. Do not reveal the other evaluator's answer before each submits. Omit implementer identity from scoring briefs and reverse the pair's presentation order between evaluators to reduce identity/order cues. This does not guarantee unbiased scores.

For the council scorecard, take the lower of the two category scores in each device/category cell. Calculate device totals and the 70/30 aggregate from this combined matrix, using unrounded values. Do this for both versions. This conservative rule is fixed before baseline scoring; do not switch aggregation methods to make a candidate win.

Retain the individual matrices for the acceptance rule in SKILL.md. Missing evidence or an incomplete evaluator response leaves scoring pending; do not invent a verdict or substitute implementation self-scores.

Use each council's paired previous-best/candidate delta to decide progress. Keep the earlier score rows intact. Target checks use the retained best's combined matrix, including the baseline; a rejected candidate cannot satisfy the target. Disagreements feed the next implementation round; do not add debate or tie-break review loops.

Keep a short record of the retained best and each failed hypothesis so the next provider tries a different fix rather than repeating a rejected candidate. Never change the rubric, hide essential content, or weaken journey checks to raise the score. The [research notes](../../../docs/ux-loop-research.md) explain the borrowed loop ideas and their limits.
