# Alternating implementers, independent scoring

Use one Codex and one Claude evaluator for the baseline and every candidate. Keep the same requested model pair and rubric throughout. Evaluators are fresh agents, separate from the current implementation agent, even when they share its provider. Start their contexts from the scoring brief without inheriting the coordinator's conversation. They inspect only and start no nested agents. An evaluator-only request ends after evaluation without implementation rounds.

Implementation alternates Codex → Claude → Codex → Claude, or starts with Claude when requested. This is a serial handoff: the previous writer stops before the next starts. The coordinator sends the retained version, latest matrices and feedback, chosen priority, scope/data/capture conditions, gaps, check results, round number, and no-progress count. Do not make the next implementer rediscover the baseline.

Send both evaluators the same matched screenshots, running interface, rubric, diff, and check results, plus each evaluator's own provider's previous matrix for the retained best, never the other provider's. Ask them to inspect the rendered images and affected journey, explain every changed score, and return both matrices, aggregates, priorities, and a verdict. Keep the desired score, target-met status, and implementer identity out of scoring briefs and attachments. Do not reveal the other evaluator's answer before each submits. Reverse the pair's presentation order between evaluators to reduce order cues. Previous matrices aid continuity but can anchor scores; concrete observations and the current paired comparison take precedence.

## Reference comparisons

When the user supplies competitor examples or asks to beat another product, retain a fixed set of reference screenshots alongside the original baseline and current pair. Agree on relevant surfaces and capture conditions before scoring; do not choose weaker examples as the candidate improves. Judge visible reference design with the same categories, keeping partial observations separate from the app's journey scores. Missing competitor interaction evidence does not imply a working journey.

Have each evaluator compare the candidate, previous best, and references in the same pass. Report paired gains and reference rankings separately. A higher score for an unchanged reference is calibration drift, not product progress. Keep historical rows intact, explain changed ratings with observations, and use current paired comparisons rather than subtracting scores from different rounds. A changed reference set starts a separate comparison series within the remaining budget. Keep brand names out of image labels when practical.

## Retain the best

For the council scorecard, take the lower of the two category scores in each device/category cell. Calculate device totals and the 70/30 aggregate from this combined matrix, using unrounded values. Do this for both versions. This conservative rule is fixed before baseline scoring; do not switch aggregation methods to make a candidate win.

Retain the individual matrices for the acceptance rule in SKILL.md. Missing evidence or an incomplete evaluator response leaves scoring pending; do not invent a verdict or substitute implementation self-scores.

Use each council's paired previous-best/candidate delta to decide progress. Keep the earlier score rows intact. Target checks use the retained best's combined matrix, including the baseline; a rejected candidate cannot satisfy the target. Disagreements feed the next implementation round; do not add debate or tie-break review loops.

The coordinator checks requested competitor rankings as well as the numeric target. Both evaluators score every candidate; a single-model screening score cannot accept work or satisfy the target. If quota prevents the full council, apply ds-work's blocker and budget rules instead of silently reducing the roster.

Keep a short record of the retained best and each failed hypothesis so the next provider tries a different fix rather than repeating a rejected candidate. Never change the rubric, hide essential content, or weaken journey checks to raise the score. The [research notes](../../../docs/ux-loop-research.md) explain the borrowed loop ideas and their limits.
