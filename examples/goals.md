# Write goals that end

An open-ended request such as “make the service faster” needs a metric, a target, and a budget before an agent can decide it is done.

Give the agent:

- The measurement command and conditions.
- A target supported by a baseline.
- Constraints that must hold throughout the work.
- A time, turn, or token budget supported by the host, plus what to do when blocked.

For example:

```text
Reduce the parser benchmark's median time by at least 10% from the current baseline, using three matched before/after runs of the existing benchmark. Preserve accepted input and error behavior. Spend at most two implementation attempts; stop and report the result if host noise hides the change or the budget ends.
```

Use the host's current goal controls when you want work to persist across turns. A prompt-level budget is useful guidance, but only the host can enforce a resource limit. Do not create a persistent goal merely because a task is large.
