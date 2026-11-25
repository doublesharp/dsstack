<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/doublesharp-dark.svg">
    <img src="assets/brand/doublesharp-light.svg" width="420" height="90" alt="doublesharp">
  </picture>
</p>

<h1 align="center">dsstack</h1>

<p align="center">16 core skills and an optional security skill for Codex and Claude, with a Python standard-library installer.</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#skills">Skills</a> ·
  <a href="#private-configuration">Private configuration</a> ·
  <a href="#development">Development</a>
</p>

---

Copy a skill folder or install the collection as a bundle. Each folder contains a `SKILL.md` and any references or scripts the skill needs. Agents can select a skill from its description, or you can name it in your request.

```text
Use $ds-debug to investigate this failure.
```

## Quick start

From the repository root, use Python 3.9+ and Git to build a bundle. The commands without `--apply` show what will happen before you make changes. Replace `~/.agents/skills` with your host's skill directory if needed, such as `~/.claude/skills` for Claude Code.

```sh
# Preview and build a bundle.
python3 scripts/dsstack.py bundle --dest .local/bundles/v1
python3 scripts/dsstack.py bundle --dest .local/bundles/v1 --apply

# Preview, install, and check the links.
python3 .local/bundles/v1/scripts/dsstack.py install --dest ~/.agents/skills
python3 .local/bundles/v1/scripts/dsstack.py install --dest ~/.agents/skills --apply
python3 .local/bundles/v1/scripts/dsstack.py doctor --dest ~/.agents/skills
```

Start a fresh agent session after installation. Keep the bundle in a durable location because the host's skill directory contains symlinks to its files. The installer checks for conflicts before changing links.

### Updating an installation

1. Build the candidate at a new path. Add `--compare <active-bundle>` to `bundle` to see which skill files the candidate omits. `BUNDLE.json` records the source revision, working tree status, and selected optional skills.
2. For each host, preview `uninstall` from the old bundle and `install` from the candidate. The candidate reports old links it would replace as conflicts. Check each conflict against the uninstall plan and resolve any others before switching.
3. Apply the old bundle's `uninstall`, then apply the candidate's `install`. Run `doctor --dest` from the candidate using the same host directory. Check any separately installed optional skill's link and start a fresh agent session.

Keep the previous bundle for rollback. To switch back, uninstall the candidate first, then reinstall the previous bundle.

For development, running `install` from the source checkout links the host directly to the files you edit.

## Skills

Start with `ds-work`, `ds-debug`, `ds-tdd`, and `ds-review`. Choose domain skills for the code you're changing.

| Area | Skills | What they help with |
| :--- | :--- | :--- |
| Delivery | [ds-work](skills/ds-work/SKILL.md) · [ds-plan](skills/ds-plan/SKILL.md) | Task lists, plans, blockers, and handoffs. |
| Correctness | [ds-debug](skills/ds-debug/SKILL.md) · [ds-tdd](skills/ds-tdd/SKILL.md) · [ds-review](skills/ds-review/SKILL.md) | Reproduce failures, test fixes, and review concrete defects. |
| Consultation | [ds-consult](skills/ds-consult/SKILL.md) | Get independent opinions and choose a council suited to the decision. |
| Resources | [ds-resources](skills/ds-resources/SKILL.md) | Check disk capacity, schedule shared builds, and clean up task-owned output. |
| Languages & services | [ds-rust](skills/ds-rust/SKILL.md) · [ds-typescript](skills/ds-typescript/SKILL.md) · [ds-solidity](skills/ds-solidity/SKILL.md) | Rust tests, TypeScript services, and Solidity contracts. |
| Authentication | [ds-auth](skills/ds-auth/SKILL.md) | Passkey-first accounts, privileged access, recovery, sessions, and scoped client grants. |
| Interfaces | [ds-web](skills/ds-web/SKILL.md) · [ds-native](skills/ds-native/SKILL.md) | Web layouts, interaction checks, and native app lifecycle. |
| Models & design | [ds-ai](skills/ds-ai/SKILL.md) · [ds-ux](skills/ds-ux/SKILL.md) | Test model-backed features and run a scored UX improvement cycle. |
| Writing | [ds-write](skills/ds-write/SKILL.md) | Draft and edit prose while preserving facts and the writer's voice. |

Use `ds-web` for routine interface changes and `ds-ux` when the task calls for scored design iterations. Cross-provider reviews require access to the requested providers.

### Optional security skill

[ds-security](optional-skills/ds-security/SKILL.md) covers dependency vulnerability checks and patches, focused security reviews, and requested codebase audits. Select it explicitly to add it to a bundle. To invoke it, ask `Use $ds-security to check and patch vulnerable dependencies.`

For an installation with private policy in `.local/policy`, run these commands. Omit `--local .local/policy` if you use the public defaults.

```sh
python3 scripts/dsstack.py bundle --dest .local/bundles/security-v1 --local .local/policy --include-optional ds-security
python3 scripts/dsstack.py bundle --dest .local/bundles/security-v1 --local .local/policy --include-optional ds-security --apply
```

The bundle includes `ds-security` in its standard `install` command. To install directly from the source checkout, add `--include-optional ds-security` to `install`. You can also copy `optional-skills/ds-security/` on its own with its license and attribution. If you already use a bundle, follow [Updating an installation](#updating-an-installation).

## Private configuration

Keep machine settings and personal additions in ignored `.local/`. When building inside the checkout, choose a new path under `.local/` and keep the directory untracked. You can also build outside the checkout.

```text
dsstack/
├── skills/                 Public, portable skill folders
├── optional-skills/        Skills selected explicitly at installation
├── scripts/                Bundle and installation tools
├── docs/                   Design, validation, and customization
└── .local/                 Private and ignored by Git
    ├── policy/             Shared rules and per-skill additions
    ├── bundles/            Stable assembled installations
    ├── tools/              Private helpers
    └── backups/            Recovery material
```

Put shared additions in `.local/policy/policy.md`, per-skill additions in `.local/policy/skills/<skill-name>.md`, and capacity settings in `.local/policy/resource-profile.json`. Pass the policy directory when you build the bundle.

```sh
python3 scripts/dsstack.py bundle --dest .local/bundles/personal-v1 --local .local/policy
python3 scripts/dsstack.py bundle --dest .local/bundles/personal-v1 --local .local/policy --apply
```

The bundler appends private rules to the relevant `SKILL.md` files. Use global or project instructions for rules that must apply even when no skill loads.

[Customization guide](docs/customization.md)

<details>
<summary><strong>Codex, Claude, and provider metadata</strong></summary>

`SKILL.md` holds the instructions for both hosts. Optional `agents/openai.yaml` files supply OpenAI interface metadata. See the [OpenAI](https://developers.openai.com/codex/skills#optional-metadata) and [Claude](https://code.claude.com/docs/en/skills) documentation.

</details>

<details>
<summary><strong>Checking disk capacity</strong></summary>

```sh
python3 skills/ds-resources/scripts/preflight.py --scratch /path/to/build-volume --project app --task parser-fix --expected-gib 20
```

Preflight checks the output root, task paths, and free space before you create directories or schedule a build. Use `--scratch` to supply a root when your profile leaves it unset. The root must be a mount unless the profile allows an ordinary directory. A command-line reserve must meet or exceed the profile's reserve. [Example resource profile](examples/resource-profile.json)

</details>

## Development

Set `TMPDIR` to an existing task-owned output directory under the project's build policy before running the tests. [AGENTS.md](AGENTS.md)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/dsstack.py doctor
```

Use the decision scenarios to compare how agents act under the current and previous skill text. [Decision scenarios](evals/scenarios.md) · [Validation guide](docs/validation.md)

---

[Design rationale](docs/focus.md) · [Sources and adaptations](docs/provenance.md) · [Source lock](upstreams.lock.json) · [License notices](licenses) · [MIT license](LICENSE)
