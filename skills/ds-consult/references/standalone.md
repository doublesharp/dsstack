# Standalone route

Use this only outside T3, where running the other provider's CLI directly is allowed. Check the installed CLI's help before using version-specific flags. Help shows syntax but not which models your account can use, so confirm the model you plan to request. Keep existing authentication, sandbox, approval, and project rules. Never bypass a permission or retry a denial through another route.

Put the brief and output in the project's configured disposable-output location. Write a fresh, nonempty brief for each consult.

Codex consulting Claude, read-only:

```sh
claude -p --no-session-persistence --model MODEL --permission-mode plan --disallowedTools "Edit,Write" < BRIEF
```

Replace `MODEL` and `BRIEF` with checked values. In Codex, launch Claude through host escalation with a short justification and `prefix_rule: ["claude"]` where supported. Host permission doesn't widen Claude's own tool permissions. Scope the task and completion condition in the brief; don't add permission-bypass flags.

Claude consulting Codex, read-only:

```sh
codex exec --ephemeral --sandbox read-only --cd REPO --model MODEL --output-last-message OUTPUT - < BRIEF
```

Use the exact repository, a checked model, and the configured output paths. Keep user and project config active, and don't add ignore-config, ignore-rules, or bypass flags.

Run one CLI process per consult and follow it to completion. Silence alone doesn't justify starting a second one. A consult counts only when the process exits successfully with the requested answer. Timeouts, interruptions, exhausted budgets, and partial streams don't count. Keep raw output in the configured output location and report findings that hold up after checking them.
