---
name: "ds-debug"
description: "Use when a test fails unexpectedly, runtime behavior is wrong, or a flaky failure needs a reproducible cause."
---

# Diagnose before changing behavior

Capture the smallest reliable reproduction: exact checkout, command or interaction, expected result, observed failure, and relevant environment. Read the complete decisive error and nearby context. Separate compile/setup failures from behavioral failures, and distinguish source reasoning from observed runtime evidence.

Trace the failing value or state across the nearest boundary. Compare a working case when available. Form one causal hypothesis that predicts a specific observation, then run the cheapest discriminating check. Change one meaningful variable at a time. Record what the result rules in or out; repeated retries without a new hypothesis add little evidence.

Use existing project wrappers and focused targets. Batch observations that share an expensive build. If instrumentation is needed, keep it scoped and remove task-only probes after obtaining the evidence. Do not broaden to an entire workspace, replace dependencies, or redesign adjacent code merely because the first hypothesis failed. Expand when an observed interaction or concrete risk requires it.

Once a cause is supported, add a behavioral regression at the relevant boundary, observe its valid failure, apply the smallest coherent fix, and verify it passes. Check neighboring behavior that shares the causal path. A mocked or copied-source check proves only that layer; preserve required browser, native, database, concurrency, and provider gates.

When a prerequisite is unavailable, state the missing evidence and continue independent work. If several hypotheses fail, reassess the model and evidence before stacking more patches. Escalate an architectural question only with the observations that make it material to the request.

Inspiration: Superpowers' systematic-debugging practice. The goal is a supported cause and verified correction, not a quota of diagnostic steps.
