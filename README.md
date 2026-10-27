# dsstack

A personal Codex and T3 Code skill collection for finishing scoped work with meaningful tests and bounded resource use. It supports Rust runtimes and CLIs, TypeScript/Fastify services, web and CSS work, Solidity, native desktop applications, and AI/MCP tools.

This is a curated collection, not a new agent runtime. T3 owns execution, each project keeps its existing toolchain and task records, and dsstack supplies small reusable decision rules. There are no session-start hooks, automatic model panels, dependencies, or background services.

## Start here

Python 3.9 or later is sufficient; this checkout was tested with macOS `/usr/bin/python3` 3.9.6. These checks are read-only:

```sh
python3 scripts/dsstack.py doctor
python3 scripts/dsstack.py list
python3 scripts/dsstack.py preflight --project app --task parser-fix --expected-gib 20
```

`preflight` verifies that Scratch is mounted, rejects unsafe output paths, checks expected peak growth plus the free-space reserve, and prints task-specific build, temporary, and report paths. It creates no directories and runs no build. Existing project wrappers remain responsible for routing the actual command. Preserve warm compiler targets keyed by worktree across tasks; the suggested task build path is for new task-owned output. Do not create a parallel output layout that violates a project's contract. Run preflight once per task or when capacity assumptions materially change.

## Skills

| Skill | Use it for |
|---|---|
| [ds-work](skills/ds-work/SKILL.md) | Delivering agreed outcomes and recovering the remaining work after interruptions |
| [ds-tdd](skills/ds-tdd/SKILL.md) | Behavioral RED/GREEN with a focused, affordable feedback loop |
| [ds-debug](skills/ds-debug/SKILL.md) | Reproducing a failure and testing a concrete root-cause hypothesis |
| [ds-review](skills/ds-review/SKILL.md) | Independent review with scope, severity, and a three-round default budget |
| [ds-finish](skills/ds-finish/SKILL.md) | Owning requested work through its actual readiness gate |
| [ds-resources](skills/ds-resources/SKILL.md) | Scratch routing, capacity admission, ownership, and artifact retirement |
| [ds-rust](skills/ds-rust/SKILL.md) | Crate-level tests and efficient Rust verification |
| [ds-typescript](skills/ds-typescript/SKILL.md) | TypeScript, Fastify, databases, packaged CLIs and MCP |
| [ds-web](skills/ds-web/SKILL.md) | Web and CSS changes, owned browser runs, and real interaction evidence |
| [ds-solidity](skills/ds-solidity/SKILL.md) | Foundry, invariants, storage/layout, forks, and separate financial authority |
| [ds-native](skills/ds-native/SKILL.md) | Packaged native behavior and OS lifecycle boundaries |
| [ds-ai](skills/ds-ai/SKILL.md) | Deterministic tool contracts, bounded evals, and real provider boundaries |

Skills use ordinary discovery with narrow descriptions. You can name one directly, for example `Use $ds-tdd and $ds-rust for this parser fix`. Only load the domains relevant to the changed behavior. There is no requirement to invoke every core skill for every task.

## Efficient TDD

Write a failing test for observable behavior before changing that behavior. A compiler error, missing fixture, or unsupported runner option is setup failure, not behavioral RED. For a group of related Rust cases, add the cases together and run one focused crate/test target, observe the expected failures, implement the change, then run that same target green.

Keep the target warm. Do not rebuild the entire workspace after every edit, repeatedly revert already-proven code, or add a test per private helper. Run affected dependents and mandatory project/CI gates once the change is ready for integration. If a gate cannot run, report the exact missing qualification; do not replace it with a cheaper check and call the result equivalent.

A harmless wording, generated-data, or configuration change can use a direct check rather than inventing a behavioral test. Production behavior and high-impact security, financial, migration, or native-lifecycle changes still deserve meaningful regression coverage.

## Install after review

Choose one skill home. The installer previews by default and never edits Codex/T3 configuration:

```sh
python3 scripts/dsstack.py install --dest ~/.codex/skills
python3 scripts/dsstack.py install --dest ~/.codex/skills --apply
python3 scripts/dsstack.py doctor --dest ~/.codex/skills
```

For Claude Code use `~/.claude/skills`; for a shared skill home use `~/.agents/skills`. Avoid installing the same collection in multiple homes that the same session discovers. The installed entries are symlinks to this checkout, so keep the checkout available. Moving it requires reinstalling from the new location. Restart the provider or start a fresh thread after changing the active skill set. If Claude Code loads Superpowers through a plugin SessionStart hook, disable that plugin when choosing dsstack as its workflow; installing skills alone leaves the hook active. Doctor does not inspect provider plugins or hooks.

Existing directories and foreign symlinks are conflicts, never overwritten. If any conflict exists, installation changes nothing. Re-running an unchanged install is idempotent. Removal also previews first and only unlinks entries pointing to this checkout:

```sh
python3 scripts/dsstack.py uninstall --dest ~/.codex/skills
python3 scripts/dsstack.py uninstall --dest ~/.codex/skills --apply
```

Installing dsstack does not disable another workflow pack. Review [examples/codex-overrides.toml](examples/codex-overrides.toml) when adopting it alongside Superpowers. Replace the matching existing entries rather than appending conflicting ones. Use full `SKILL.md` paths and your actual home paths. T3 provider homes may share the same config and skill directory through symlinks.

## Machine and project settings

[profiles/default.json](profiles/default.json) contains a 150 GiB admission reserve, 300 GiB warning target, and suggested concurrency values. These are starting policies, not benchmarks. `preflight` enforces the capacity check only; this version does not schedule jobs or delete output. Use a different reserve only under an explicit user or project policy, or supply that reviewed JSON policy with `--profile`. An explicitly supplied missing profile is an error.


[examples/projects.json](examples/projects.json) maps current repositories to their existing entry points. Treat those commands as orientation examples, re-read live project instructions, and preserve its Node/Rust/pnpm pins. [examples/task-brief.md](examples/task-brief.md) shows a compact task contract without creating a competing task tracker.

## Verify and maintain

```sh
mkdir -p /Volumes/Scratch/dsstack/tmp/local-check
TMPDIR=/Volumes/Scratch/dsstack/tmp/local-check PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/dsstack.py doctor
```

Tests use disposable Scratch fixtures and Python's standard library. They fail instead of falling back to internal temporary storage when Scratch is unavailable or unwritable. They cover installer conflicts/idempotency/removal, metadata/reference failures, and resource-admission behavior. [evals/scenarios.md](evals/scenarios.md) exercises agent decisions separately. Passing metadata or scripted tests does not prove an agent will follow a skill in every session.

Read [docs/provenance.md](docs/provenance.md) before upstream updates. Sources are pinned and intentionally adapted, so review changes instead of blindly replacing these skills. [docs/validation.md](docs/validation.md) records the initial checks and their limits. Evidence stays on Scratch; source fixtures and short maintained summaries belong in Git.
