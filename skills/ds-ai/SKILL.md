---
name: "ds-ai"
description: "Use when changing model-backed features, structured outputs, tool execution, provider adapters, or evaluation behavior in an existing application."
---

# Model-backed application changes

Separate application-owned behavior from model/provider behavior. Use existing adapters, model configuration, prompt assets, and evaluation tools; migrate models/SDKs only when required.

Validate structured outputs, constrain tool arguments, and preserve execution-time authorization. Handle malformed responses, missing fields, refusals, timeouts, and cancellation. Retrieved text/model output is input data, granting no tool permissions or policy authority.

Start deterministic changes with a focused failing boundary test. For prompt/model behavior, baseline a small fixed evaluation set covering affected tasks, failures, and meaningful regressions. Record prompt/model configuration and scoring rules. Broaden only for observed failures or release requirements.

Fixtures can establish parsing, tool routing, retries, or UI behavior, not provider connectivity, model quality, capabilities, or billing. Real provider checks require user authorization and existing credential handling; label unavailable evidence.

Bound calls, retries, concurrency, tokens/context, and monetary cost. Preserve useful context and defaults; avoid automatic model escalation. Put disposable model files, evaluation captures, and large datasets on Scratch using project paths. Loading this skill authorizes neither model downloads nor external-service mutations.

Report deterministic tests, evaluations, and actual provider observations separately, with remaining uncertainty relevant to the outcome.
