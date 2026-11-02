# Open-ended targets and goals

## Asks without a number

For asks like "make it faster", "raise coverage", or "beat the other bots", choose a metric, a baseline, a target, and a budget, and state them before you start. Stop at the target, at the budget, or after two attempts that don't move the number. If run-to-run noise hides the gain, say so instead of building a better benchmark.

## Under a goal or stop hook

Claude's `/goal` and Codex goals start a new turn whenever one ends, until the goal's condition holds. Ending a turn doesn't stop the work.

- If the goal has no number, state your metric, target, and budget in the first goal turn, and work to them.
- If you create a goal, put the target and budget in its objective.
- A checker's "not met" verdict describes what it couldn't see in the conversation. Show the measurement if you have it, and don't treat the verdict as a new requirement.
- To stop at the target, at the budget, or at a blocker only the user can clear, say so in one message and stop calling tools. Claude ends the loop after a few turns without tool use. In Codex, mark the goal complete when its objective is met, or blocked once its rule allows.
