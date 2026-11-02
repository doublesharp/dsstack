# dsstack

Personal skills for Codex, Claude Code, and T3 Code that keep coding agents on the ask. They work one item at a time, run checks when a result can still change a decision, and end with a short handoff. Domain skills cover Rust, TypeScript and Fastify services, web and CSS, Solidity, native desktop apps, and AI/MCP features.

This is a set of instructions, not an agent runtime. The host app runs the agents, each project keeps its own toolchain and tracker, and there are no session-start hooks, background services, or dependencies.

## How the skills keep work moving

These rules come from this machine's own session logs and from published guidance. [docs/focus.md](docs/focus.md) has the numbers and the sources.

- One item in progress per agent. Each item has a done-when check and ends as done, blocked, or dropped. Discovered work becomes a follow-up.
- Fast checks while editing. Slow checks run once, after the last edit they cover, and a pass holds until something it covers changes.
- Counted limits instead of judgment calls. After two failed fixes, two wrong debugging hypotheses, or one or two tries at an environment problem, the agent changes approach or reports a blocker.
- One review of the finished diff and one re-check of its must-fix fixes. Everything else is a follow-up.
- Commits, the item list, and the final message are the record. Agents don't produce receipts, manifests, or evidence packets unless asked.

## Skills

| Skill | Use it for |
|---|---|
| [ds-work](skills/ds-work/SKILL.md) | Multi-part or long-running delivery, resuming, and handoff |
| [ds-plan](skills/ds-plan/SKILL.md) | Specs and plans for unclear or large requests |
| [ds-tdd](skills/ds-tdd/SKILL.md) | A failing test first for behavior changes and regressions |
| [ds-debug](skills/ds-debug/SKILL.md) | Finding the cause of a failure before fixing it |
| [ds-review](skills/ds-review/SKILL.md) | Reviews sorted into must-fix and follow-up, with a round limit |
| [ds-consult](skills/ds-consult/SKILL.md) | Codex and Claude cross-reviews and requested councils |
| [ds-resources](skills/ds-resources/SKILL.md) | Where worktrees and build output go, and Scratch capacity checks |
| [ds-rust](skills/ds-rust/SKILL.md) | Crate-level Rust tests and warm builds |
| [ds-typescript](skills/ds-typescript/SKILL.md) | TypeScript packages, Fastify, databases, CLIs, and MCP |
| [ds-web](skills/ds-web/SKILL.md) | Web and CSS changes and the browser checks they need |
| [ds-solidity](skills/ds-solidity/SKILL.md) | Foundry tests, invariants, upgrades, forks, and fund safety |
| [ds-native](skills/ds-native/SKILL.md) | Packaging, OS permissions, and native lifecycles |
| [ds-ai](skills/ds-ai/SKILL.md) | Model-backed features, evals, and provider boundaries |

Agents pick skills by their descriptions and load only the ones that fit. You can also name them, for example `Use $ds-work and $ds-rust for the parser items in the tracker`.

## Install and update

Python 3.9 or later is enough. Each command previews its changes until you add `--apply`.

```sh
python3 scripts/dsstack.py install --dest ~/.agents/skills
python3 scripts/dsstack.py install --dest ~/.agents/skills --apply
python3 scripts/dsstack.py install --dest ~/.claude/skills --apply
python3 scripts/dsstack.py doctor --dest ~/.agents/skills
python3 scripts/dsstack.py doctor --dest ~/.claude/skills
```

`~/.agents/skills` serves Codex, including T3's Codex provider homes. `~/.claude/skills` serves Claude Code, including T3's Claude sessions. Installed skills are symlinks to this checkout, so a change goes live as soon as it lands here, and the checkout has to stay where it is. Install adds links for new skills and prunes links to skills this checkout no longer ships. It never replaces an existing directory or a link that points elsewhere, and any such conflict stops the whole install. Uninstall removes only links into this checkout. Start a fresh thread after the skill set changes.

[examples/codex-overrides.toml](examples/codex-overrides.toml) lists the Superpowers workflow skills this pack replaces. [examples/always-on.md](examples/always-on.md) is a block for the global AGENTS.md and CLAUDE.md, which the installer doesn't apply. [examples/goals.md](examples/goals.md) shows how to write Claude and Codex goals that end. [docs/trial.md](docs/trial.md) records the original activation and its archive.

## Resource preflight

```sh
python3 scripts/dsstack.py preflight --project app --task parser-fix --expected-gib 20
```

Preflight checks that Scratch is mounted, that the task's output paths are safe, and that free space covers the expected peak plus the reserve in [profiles/default.json](profiles/default.json). It creates nothing and schedules nothing, and project wrappers still route the real builds.

## Maintain

```sh
mkdir -p /Volumes/Scratch/dsstack/tmp/local-check
TMPDIR=/Volumes/Scratch/dsstack/tmp/local-check PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/dsstack.py doctor
```

The tests use Scratch fixtures and the standard library. They cover installer conflicts, idempotency, pruning, owned removal, metadata and reference errors, and preflight decisions. Passing them says nothing about whether agents follow the skills. [evals/scenarios.md](evals/scenarios.md) and the session measures in [docs/focus.md](docs/focus.md) cover that. Read [docs/provenance.md](docs/provenance.md) before pulling in upstream changes, and [AGENTS.md](AGENTS.md) before editing a skill.
