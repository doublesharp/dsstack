# Open-ended targets and goals

## Asks without a number

For asks like "make it faster", "raise coverage", choose a metric, a baseline, a target, and a budget, and state them before you start. Stop at the target, at the budget, or after two attempts that don't move the number. If run-to-run noise hides the gain, say so instead of building a better benchmark.

## Under a goal or stop hook

A host goal or stop hook may continue after the current turn. Use its actual completion, budget, and blocker rules; ending a turn alone may not stop it.

- If the goal has no number, state your metric, target, and budget in the first goal turn, and work to them.
- If you create a goal, put the target and budget in its objective.
- A checker's "not met" verdict describes what it couldn't see in the conversation. Show the measurement if you have it, and don't treat the verdict as a new requirement.
- At the target, budget, or a blocker only the user can clear, report the result and use the host's supported stop mechanism. Mark a goal complete only when its objective is met; mark it blocked only when the host's rule allows. Don't keep running checks to satisfy an automatic continuation.
