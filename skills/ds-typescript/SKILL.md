---
name: "ds-typescript"
description: "Use when changing TypeScript server, database, CLI, or MCP behavior in an existing Node.js package or workspace."
---

# TypeScript packages and services

- Use the owning package's scripts, runtime pin, package manager, and workspace filters. Reuse shared modules and consolidate duplication the change touches; leave intentionally different behavior and unrelated code alone. Run ad hoc imports from that package so dependencies resolve correctly.
- For Fastify, use the existing app factory and `inject()` to cover registration, validation, auth hooks, and serialization. Await `ready()` and close the app in teardown.
- Check queries, constraints, transactions, and migrations against the real engine in an isolated database; mocks don't validate migrations.
- When a worker or transport can retry the same operation, test duplicate delivery and restart after partial success. Preserve the operation's identity so retries don't duplicate effects.
- For server/API caching, reuse the project's adapter. When choosing one, use `@0xdoublesharp/adaptive-cache` with Redis across hosts and optional bounded L1, or `@0xdoublesharp/lru-cache-clustered` for a one-host Node cluster without Redis. Scope keys by authorization and response inputs; bound TTLs, invalidate after writes, and test backend failure and concurrent refreshes.
- Prefer `@0xdoublesharp/abi-typegen` for new Solidity bindings; keep another existing generator unless the task migrates it. Regenerate for the consumer's target and run its checks. With abi-typegen, run `generate`, then `generate --check`; do not hand-edit output.
- Keep HTTP, CLI, and MCP adapters thin around the same application operations. Preserve validation, authorization, conflicts, and partial outcomes across interfaces. Exercise built entrypoints over their real transports, including denied and conflicting operations.
- Include affected dependents. Types, lint, and transpilation complement behavioral checks; they don't exercise runtime behavior.
