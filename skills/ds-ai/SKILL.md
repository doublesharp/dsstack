---
name: "ds-ai"
description: "Use when changing model-backed features, structured outputs, tool execution, provider adapters, or evaluation behavior in an existing application."
---

# Model-backed application changes

Identify the behavior the application owns and the behavior supplied by the model or provider. Use existing provider adapters, model configuration, prompt assets, and evaluation tools. Keep a model or SDK migration outside the change unless the requested behavior requires it.

Make deterministic boundaries explicit: validate structured output before use, constrain tool arguments, preserve authorization at execution time, and handle malformed responses, missing fields, refusals, timeouts, and cancellation. Treat retrieved text and model output as input data; they do not grant permission to execute tools or change application policy.

For deterministic application changes, begin with the smallest failing boundary test. For prompt or model-dependent behavior, establish a baseline with a small fixed evaluation set representing the affected tasks, failure cases, and meaningful regressions. Record the prompt/model configuration and a clear scoring rule. Broaden the set when observed failures or release requirements justify it, rather than running a large benchmark on every edit.

Fixture responses can establish parsing, tool routing, retries, and UI behavior. They do not prove real provider connectivity, model quality, supported capabilities, or billing behavior. Use a real provider check only within the user's authorization and existing credential handling; label unavailable provider evidence explicitly.

Bound calls, retries, concurrency, token/context use, and monetary cost for the task. Preserve useful context and project defaults rather than adding automatic model escalation. Store disposable model files, evaluation captures, and large datasets on Scratch using project paths. Do not download models or mutate external services merely because this skill is loaded.

Report deterministic tests, evaluation results, and actual provider observations as separate evidence, including the remaining uncertainty relevant to the requested outcome.
