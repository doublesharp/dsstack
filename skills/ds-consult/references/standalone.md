# Standalone route

Use only outside T3 when direct CLI consultation is permitted. Inspect installed CLI help and model discovery before using version-specific flags. Help confirms syntax, not model availability. Preserve existing authentication, sharing authorization, sandbox/approval rules, and project instructions. Never bypass permissions or retry a denial through another route.

Create the brief and output directory under `/Volumes/Scratch/<project>/reports/<task>/`; stop if Scratch is missing. Use a fresh, scoped prompt and require a nonempty brief. Verify requested model identifiers rather than treating family aliases as version proof.

**Codex → Claude:** the locally documented read-only invocation is:

```sh
claude -p --no-session-persistence --model MODEL --permission-mode plan --disallowedTools "Edit,Write" < BRIEF
```

Replace `MODEL` and `BRIEF` with verified values. In Codex, launch Claude through host escalation with a scoped justification and `prefix_rule: ["claude"]` where supported. Host permission does not widen Claude's tool permissions. Never use permission-bypass flags or turn limits for Opus/Fable; bound the task in its brief.

**Claude → Codex:** installed `codex exec --help` supports:

```sh
codex exec --ephemeral --sandbox read-only --cd REPO --model MODEL --output-last-message OUTPUT - < BRIEF
```

Use the exact trusted repository, verified model, and Scratch paths. Keep user/project config and execution rules active; do not add ignore-config, ignore-rules, or bypass flags.

Maintain one CLI process per consultation. Follow that process through completion; silence alone does not justify a duplicate. Require successful exit plus the requested final result, then verify findings locally. A timeout, interrupted run, exhausted budget, or partial stream is incomplete. Preserve raw output on Scratch; report only relevant findings and proof limits.
