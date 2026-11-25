# Why these rules exist

These rules grew out of recurring problems in coding sessions. [Sources and adaptations](provenance.md)

| Failure | Response |
|---|---|
| A task grows while the agent works | Finish one requested item at a time and record discoveries as follow-ups |
| Later edits invalidate slow checks | Run focused checks while editing and broader required checks after the relevant edits |
| Each review creates another review | Tie findings to a triggering scenario and limit re-checks |
| Repeated fixes obscure the cause | A counted attempt limit, then diagnosis or a clear blocker |
| An open-ended goal has no finish | A metric, target, and budget before iteration |
| Reporting becomes its own project | A short handoff unless the task needs more |
| Guessed file paths or wrong package roots fail repeatedly | Locate files in the current checkout and run imports from the owning package |

Each skill can run on its own. Narrow descriptions help agents select specialized workflows for the tasks that need them. [Skill catalog](../README.md#skills)

## Evaluating an installation

The observations came from sessions that varied by project, model, instructions, and task difficulty. Use comparable tasks to measure changes in completion rates or time spent.

Try the decision scenarios before normal work, then inspect a small sample of completed tasks. Check whether agents finished the requested work, ran the required checks, repeated review rounds, or spent time on unrelated work. Keep examples of failures and store raw session records privately. [Decision scenarios](../evals/scenarios.md)

## Custom policy belongs outside the defaults

Put machine paths, hardware reserves, hosting rules, and personal preferences into your private bundle. That keeps the same public skills usable across machines and projects. [Private customization](customization.md)
