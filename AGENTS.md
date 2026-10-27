# Working on dsstack

Build a small, portable collection of skills for scoped delivery and proportionate verification.
The user authorized implementation through a completed reviewable stack in this session.

- Keep skill descriptions narrow. No automatic session-start router or mandatory agent fan-out.
- Favor behavioral TDD for code changes. Use focused tests in the inner loop; run broader required checks at integration boundaries. Do not add tests that only mirror skill wording.
- Use Python standard-library tooling so maintaining this stack needs no compiler, package download, or build cache.
- Run generated fixtures, logs, bytecode, and test output under /Volumes/Scratch/dsstack. Set TMPDIR and PYTHONDONTWRITEBYTECODE=1 for tests.
- Skills do not grant permission to merge, deploy, delete data, send messages, or bypass harness policy.
- Preserve other projects and installed global skills. Provide an explicit, dry-run-first installer.
- Document borrowed ideas and exact upstream sources. Keep license notices for adapted material.
- Scope validation to changed behavior and mandatory checks. Once those pass, finish the requested work.
