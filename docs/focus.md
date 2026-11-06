# Why these rules exist

The skills grew from recurring problems in real coding sessions: repeated review rounds, checks invalidated by later edits, environment troubleshooting that outlasted the task, and unrelated work expanding the assignment. Published guidance informed the response; exact sources are in [provenance.md](provenance.md).

The collection makes a few deliberate choices:

| Failure | Response |
|---|---|
| A task grows while the agent works | One requested item in progress; discoveries become follow-ups |
| Slow checks run before the code settles | Focused checks while editing; broader required checks after relevant edits |
| Each review creates another review | Findings tied to a triggering scenario; a bounded re-check |
| Repeated fixes obscure the cause | A counted attempt limit, then diagnosis or a clear blocker |
| An open-ended goal has no finish | A metric, target, and budget before iteration |
| Reporting becomes its own project | A short handoff unless the task needs more |
| Guessed file paths or wrong package roots fail repeatedly | Locate files in the current checkout and run imports from the owning package |

Each skill includes enough guidance to run alone. General delivery belongs to ds-work, model councils to ds-consult, and UX scoring and round budgets to ds-ux. Narrow descriptions keep ordinary tasks from activating specialized workflows.

## What has been measured

Local session observations motivated these rules. They are not a controlled benchmark: projects, models, instructions, and task difficulty changed between periods. The public collection makes no numerical claim about time saved or completion rates.

To evaluate an installation, use [decision scenarios](../evals/scenarios.md) before normal work, then inspect a small sample of completed tasks. Look for required outcomes finished, relevant checks passed, repeated review chains, and time spent on unrelated work. Compare similar tasks and retain failures as examples. Keep raw session records private.

## Custom policy belongs outside the defaults

A build volume, hardware reserve, hosting contract, or personal reporting preference can be useful without being universal. [Private customization](customization.md) places those details in the assembled installation while the public skills remain portable. Changing the public source does not activate a new bundle.
