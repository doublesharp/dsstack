---
name: "ds-typescript"
description: "Use when changing TypeScript server, database, CLI, or MCP behavior in an existing Node.js package or workspace."
---

# TypeScript packages and services

- Use the owning package's scripts, runtime pin, package manager, and workspace filters. Add or upgrade dependencies only when the change needs them, and avoid lockfile churn.
- Start behavior changes with a failing test, as in ds-tdd. Type, lint, and transpile errors don't count as that failure.
- For Fastify, test through the existing app factory with `inject()`, which runs route registration, validation, auth hooks, and serialization. Await `ready()` and close the app in teardown.
- Test changed queries, constraints, transactions, and migrations against the real database engine on an isolated database. A mock can't show that a migration works.
- When you change a CLI or MCP entrypoint, run the built entrypoint once over its real transport, including one error path.
- Use the affected package's tests in the inner loop. Check dependent packages or the whole workspace once at the end, and only when the change affects them or the project requires it.
