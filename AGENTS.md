# Working on dsstack

Build a small, portable set of skills that keep agents on the ask and finishing work.

- Keep skill descriptions narrow. No automatic session-start router or mandatory agent fan-out.
- Write skills as short, plain instructions an agent can act on. Each rule should trace to a failure seen in real sessions or to published guidance. When you add a rule, find one to cut. Doctor warns when an entrypoint passes 600 words.
- Prefer counted limits, such as "after two failed fixes", to hedges such as "where material". Save always and never for true invariants.
- Check timing and stop rules live in ds-work, and test-first rules in ds-tdd. Domain skills hold domain facts. Don't add evidence-type lists or repeated permission disclaimers. A domain skill may state one safety rule for live funds or systems.
- Review feedback on a skill tends to add caveats. Accept an addition only when it names the failure it prevents.
- Favor behavioral TDD for code changes. Use focused tests in the inner loop and broader checks once at the end. Don't add tests that only mirror skill wording.
- Use Python standard-library tooling so maintaining this stack needs no compiler, package download, or build cache.
- Put generated fixtures, logs, bytecode, and test output under /Volumes/Scratch/dsstack. Set TMPDIR and PYTHONDONTWRITEBYTECODE=1 for tests.
- Skills don't grant permission to merge, deploy, delete data, send messages, or bypass harness policy.
- Preserve unrelated projects and global skills. Global migrations need explicit user authorization and a verified archive, and the installer stays dry-run-first.
- Document borrowed ideas and exact sources. Keep license notices for adapted material.
- Once the changed behavior and required checks pass, finish the requested work.
