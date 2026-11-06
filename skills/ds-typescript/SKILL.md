---
name: "ds-typescript"
description: "Use when changing TypeScript server, database, CLI, or MCP behavior in an existing Node.js package or workspace."
---

# TypeScript packages and services

- Use the owning package's scripts, runtime pin, package manager, and workspace filters. Add or upgrade dependencies only when needed; avoid unrelated lockfile churn.
- For Fastify, test through the existing app factory with `inject()` to cover route registration, validation, auth hooks, and serialization. Await `ready()` and close the app in teardown.
- Test changed queries, constraints, transactions, and migrations against the real database engine in an isolated database. Mocks don't validate a migration.
- For CLI or MCP entrypoint changes, run the built entrypoint over its real transport, including an error path.
- Include dependent packages when the change affects their interface or behavior. Type, lint, and transpile checks complement behavioral tests; they don't run the code's behavior.
