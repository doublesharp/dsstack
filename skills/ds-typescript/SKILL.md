---
name: "ds-typescript"
description: "Use when changing TypeScript server, database, CLI, or MCP behavior in an existing Node.js package or workspace."
---

# TypeScript service and package changes

Read the owning package's scripts, lockfile, runtime pin, TypeScript configuration, and existing test setup. Use the project's package manager and workspace filters. Keep dependency changes tied to the requested behavior; a package edit does not justify toolchain upgrades or lockfile churn.

Start behavioral changes with a focused failing test in the owning package. A transpile, lint, or type error is not behavioral RED. After the focused test passes, run affected package checks and the repository's required integration gate. Distinguish source typechecks from built and installed package behavior.

For Fastify routes, prefer the existing application factory and `inject()` to exercise real registration, validation, authentication hooks, serialization, and response behavior without binding another port. Await readiness and close app resources using the project's test lifecycle. Use an actual socket when transport behavior is the question.

Database queries, constraints, transaction behavior, and migrations need the project's real database integration tests when affected. Use isolated authorized test resources and the production database engine where engine behavior matters. In-memory doubles and copied schemas do not establish migration correctness. Preserve fixture setup and teardown ownership.

For CLI or MCP changes, smoke the built package through its actual entrypoint and supported transport, including initialization, errors, exit status, and cleanup relevant to the change. Calling a handler directly cannot establish package exports or protocol transport behavior.

Keep fixtures, real database behavior, and real provider calls separate in the evidence. An SDK mock can verify request construction; it cannot prove provider acceptance. Follow existing authorization and retry rules for any real external operation.
