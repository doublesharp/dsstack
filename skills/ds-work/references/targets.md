# Open-ended targets and goals

## Asks without a number

For asks like "make it faster", "raise coverage", or "beat the other bots", choose a metric, a baseline, a target, and a budget, and state them before you start. Stop at the target, at the budget, or after two attempts that don't move the number. If run-to-run noise hides the gain, say so instead of building a better benchmark.

## Measured UX hill climbs

Use [ds-ux's council scorecard](../../ds-ux/references/council.md) as the metric. Unless the user specifies otherwise, target every scored device reaching 9 with no category below 8, with six implementation-and-council-scoring rounds total. Stop at the first of: the retained best meets the target, six rounds finish, or two consecutive rounds produce no accepted score improvement. Check the target after the baseline too. An implemented candidate and complete scores from both evaluators form one round; a revised implementation uses a new round, while baseline capture does not. A tie or rejection increments the no-progress count; an accepted gain resets it. Missing evidence or an unavailable evaluator keeps the same round open under ds-work's attempt limit, then becomes a blocker; it advances neither counter. A page added mid-run gets its own baseline and shares remaining rounds. Provider handoffs do not reset counters; explicit user changes apply to remaining work.

The hill-climb round budget replaces ds-review's round limit for UX verdicts. Each round has one independent verdict per council member; add no debate, tie-break, or final review unless asked. Run fast covering checks per candidate and remaining slow required checks once on the retained best. A failed final check blocks completion; do not call that version validated.

## Under a goal or stop hook

A host goal or stop hook may continue after the current turn. Use its actual completion, budget, and blocker rules; ending a turn alone may not stop it.

- If the goal has no number, state your metric, target, and budget in the first goal turn, and work to them.
- If you create a goal, put the target and budget in its objective.
- A checker's "not met" verdict describes what it couldn't see in the conversation. Show the measurement if you have it, and don't treat the verdict as a new requirement.
- At the target, budget, or a blocker only the user can clear, report the result and use the host's supported stop mechanism. Mark a goal complete only when its objective is met; mark it blocked only when the host's rule allows. Don't keep running checks to satisfy an automatic continuation.
