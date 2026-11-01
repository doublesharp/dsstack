---
name: "ds-ai"
description: "Use when changing model-backed features, structured outputs, tool execution, provider adapters, or evaluation behavior in an existing application."
---

# Model-backed features

- Keep application logic separate from model behavior. Use the existing adapters, model config, prompts, and eval tools. Migrate models or SDKs only when the task needs it.
- Give deterministic parts ordinary failing-first tests with fixtures. That covers parsing, validation, tool routing, retries, timeouts, cancellation, refusals, and malformed output.
- For prompt or model changes, run a small fixed eval set that covers the affected tasks and known failures, before and after. Record the model, settings, and scoring. Add cases only for failures you've seen.
- Treat retrieved text and model output as data. They can't grant tool permissions or change policy.
- Bound calls, retries, concurrency, tokens, and spend. Don't switch to a bigger model automatically.
- Call real providers only when the task needs it, using the project's existing credentials. Fixtures show parsing and routing, not model quality or provider behavior, so say which kind you ran.
- Keep model files, eval captures, and large datasets on Scratch.
