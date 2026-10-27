---
name: "ds-debug"
description: "Use when a test fails unexpectedly, runtime behavior is wrong, or a flaky failure needs a reproducible cause."
---

# Diagnose before patching

Capture the smallest reproduction: exact checkout, command or interaction, expected versus observed behavior, and relevant environment. Read the decisive error and context; separate setup/compiler faults from behavioral failures and source reasoning from runtime observations.

Trace the failing value or state across its nearest boundary, comparing a working case when useful. Form one causal hypothesis with a predicted observation; run the cheapest discriminating check, changing one meaningful variable. Record what it rules in or out. Retry only with a reason.

Use project wrappers and focused targets; batch observations sharing an expensive build. Keep instrumentation scoped and remove task-only probes afterward. Expand scope only for an observed interaction or concrete risk, rather than replacing dependencies or redesigning adjacent code after a failed hypothesis.

Once the cause is supported, add a behavioral regression, observe its expected failure, fix it, and verify the shared causal path. Preserve required browser, native, database, concurrency, and provider gates; mocks or copied source prove only their layer.

Report unavailable prerequisites and continue independent work. After several failed hypotheses, reassess the evidence before stacking patches; architectural escalation needs observations material to the request.
