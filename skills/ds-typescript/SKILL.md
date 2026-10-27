---
name: "ds-typescript"
description: "Use when changing TypeScript server, database, CLI, or MCP behavior in an existing Node.js package or workspace."
---

# TypeScript service and package changes

Use the owning package's scripts, runtime pin, lockfile, TypeScript/test configuration, package manager, and workspace filters. Limit dependency changes to the requested behavior; avoid unrelated upgrades or lockfile churn.

Start behavior changes with a focused failing test; transpile, lint, and type errors are not behavioral RED. Once the test passes, run affected package checks and required integration gates. Distinguish source typechecks from built/installed behavior.

For Fastify, prefer the existing app factory and `inject()` to exercise real registration, validation, authentication hooks, serialization, and responses. Await readiness and close resources through the test lifecycle. Use sockets for transport questions.

Affected queries, constraints, transactions, and migrations need real database integration tests with isolated authorized resources and the production engine where engine behavior matters. Doubles/copied schemas cannot prove migrations. Preserve fixture setup/teardown ownership.

Smoke CLI/MCP changes through the built package's actual entrypoint and supported transport, covering relevant initialization, errors, exit status, and cleanup. Direct handlers cannot prove exports or transport.

Report fixture, database, and provider evidence separately. SDK mocks can verify request construction, not acceptance; real operations follow existing authorization and retry rules.
