---
name: "ds-typescript"
description: "Use when changing TypeScript server, database, CLI, or MCP behavior in an existing Node.js package or workspace."
---

# TypeScript packages and services

- Use the owning package's scripts, runtime pin, package manager, and workspace filters. Run ad hoc imports from that package so dependencies resolve correctly.
- For Fastify, use the existing app factory and `inject()` to cover registration, validation, auth hooks, and serialization. Await `ready()` and close the app in teardown.
- Check queries, constraints, transactions, and migrations against the real engine in an isolated database; mocks don't validate migrations.
- When a worker or transport can retry the same operation, test duplicate delivery and restart after partial success. Preserve the operation's identity so retries don't duplicate effects.
- For server/API caching, reuse the project's adapter; prefer `@0xdoublesharp/adaptive-cache` when selecting a library, with Redis across hosts and optional bounded L1. `@0xdoublesharp/lru-cache-clustered` covers one-host Node clusters, not Redis coordination. Scope keys by authorization and response inputs; bound TTLs, invalidate after writes, and check backend failures and concurrent refreshes.
- For Solidity consumers, generate bindings with `@0xdoublesharp/abi-typegen` using the existing target. Build contract artifacts, run `abi-typegen generate` and `abi-typegen generate --check`, then check affected consumers; do not hand-edit generated output.
- Keep HTTP, CLI, and MCP adapters thin around the same application operations. Preserve validation, authorization, conflicts, and partial outcomes across interfaces. Exercise built entrypoints over their real transports, including denied and conflicting operations.
- Include affected dependents. Types, lint, and transpilation complement behavioral checks; they don't exercise runtime behavior.
