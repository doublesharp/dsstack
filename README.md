<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/doublesharp-dark.svg">
    <img src="assets/brand/doublesharp-light.svg" width="420" height="90" alt="doublesharp">
  </picture>
</p>

<h1 align="center">dsstack</h1>

<p align="center"><strong>Finish the ask. Check the result. Stop.</strong></p>
<p align="center">14 focused skills · Self-contained folders · Python standard-library tooling · MIT</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#the-skills">The skills</a> ·
  <a href="#make-it-yours">Make it yours</a> ·
  <a href="#maintain">Maintain</a>
</p>

---

Small, opinionated skills for coding agents. dsstack covers delivery, debugging, reviews, and application work, with short instructions and clear stopping points. Your host supplies the models, tools, and permissions.

Each skill folder contains its instructions, references, and any helper it needs. Use one on its own or install the collection. Agents select skills by their descriptions; you can also ask directly:

```text
Use $ds-debug to investigate this failure.
```

## Quick start

**Requires Python 3.9+ and Git.** Create a stable bundle, preview its installation, then apply it:

```sh
# Preview and build a bundle.
python3 scripts/dsstack.py bundle --dest .local/bundles/v1
python3 scripts/dsstack.py bundle --dest .local/bundles/v1 --apply

# Preview, install, and check the links.
python3 .local/bundles/v1/scripts/dsstack.py install --dest ~/.agents/skills
python3 .local/bundles/v1/scripts/dsstack.py install --dest ~/.agents/skills --apply
python3 .local/bundles/v1/scripts/dsstack.py doctor --dest ~/.agents/skills
```

Use the skill directory supported by your host. `~/.agents/skills` and `~/.claude/skills` are common destinations. **Start a fresh agent session after installation.**

Installed links point into the bundle, so source edits do not change active instructions. Existing directories and foreign links are preserved; a conflict stops installation before changes. Keep bundles in a durable location.

## The skills

Start with **ds-work**, **ds-debug**, **ds-tdd**, and **ds-review**. Add domain skills for the work at hand.

| Area | Skills | What they help with |
| :--- | :--- | :--- |
| **Delivery** | [ds-work](skills/ds-work/SKILL.md) · [ds-plan](skills/ds-plan/SKILL.md) | Finish one item, plan the right scope, resume and hand off. |
| **Correctness** | [ds-debug](skills/ds-debug/SKILL.md) · [ds-tdd](skills/ds-tdd/SKILL.md) · [ds-review](skills/ds-review/SKILL.md) | Reproduce failures, check behavior, substantiate findings. |
| **Consultation** | [ds-consult](skills/ds-consult/SKILL.md) | Independent Codex/Claude opinions and requested councils. |
| **Resources** | [ds-resources](skills/ds-resources/SKILL.md) | Check capacity, route output, reclaim unused task resources. |
| **Languages & services** | [ds-rust](skills/ds-rust/SKILL.md) · [ds-typescript](skills/ds-typescript/SKILL.md) · [ds-solidity](skills/ds-solidity/SKILL.md) | Work within toolchains, databases, APIs, and contract checks. |
| **Interfaces** | [ds-web](skills/ds-web/SKILL.md) · [ds-native](skills/ds-native/SKILL.md) | Browser journeys, responsive layouts, native boundaries. |
| **Models & design** | [ds-ai](skills/ds-ai/SKILL.md) · [ds-ux](skills/ds-ux/SKILL.md) | Model-backed behavior and requested, measured UX improvement. |

The skills keep work focused:

- **One requested item at a time.** Record unrelated discoveries as follow-ups.
- **Checks that cover the change.** Use fast checks while editing; run slow required checks after the edits they cover.
- **Counted limits.** Change approach after repeated failed fixes; bound reviews and open-ended work.
- **A clear finish.** Report what changed, what passed, and what blocks the result.

Project instructions and the user's task control the work. Cross-provider consultation needs the requested providers to be available. `ds-ux` owns the opt-in scoring workflow; routine interface changes use `ds-web`.

## Make it yours

Keep reusable skills at the repository root and personal setup beside them in ignored `.local/`:

```text
dsstack/
├── skills/                 Public, portable skill folders
├── scripts/                Bundle and installation tools
├── docs/                   Design, validation, and customization
└── .local/                 Private and ignored by Git
    ├── policy/             Shared rules and per-skill additions
    ├── bundles/            Stable assembled installations
    ├── tools/              Private helpers
    └── backups/            Recovery material
```

Put shared additions in `.local/policy/policy.md`, domain additions in `.local/policy/skills/<skill-name>.md`, and optional capacity settings in `.local/policy/resource-profile.json`. Then assemble them into a new private bundle:

```sh
python3 scripts/dsstack.py bundle --dest .local/bundles/personal-v1 --local .local/policy
python3 scripts/dsstack.py bundle --dest .local/bundles/personal-v1 --local .local/policy --apply
```

Private rules are included in the relevant skill, so agents receive them without loading a separate preferences skill. Use global or project instructions for rules that must apply even when no skill loads.

**[Read the customization guide →](docs/customization.md)**

<details>
<summary><strong>Updating an installation</strong></summary>

Build at a new bundle path and compare it with the active bundle. Preview uninstalling the old bundle and installing the new one, then apply the switch. Uninstall removes only that bundle's owned links; retain the previous bundle for rollback.

An in-checkout bundle must be under ignored, untracked `.local/`; external destinations also work. Direct installation from source is supported for development and makes source edits live immediately.

The installer does not change global instructions, model settings, plugins, or permissions.

</details>

<details>
<summary><strong>Codex, Claude, and provider metadata</strong></summary>

`SKILL.md` holds the portable instructions. Optional `agents/openai.yaml` files supply OpenAI interface metadata; Claude reads `SKILL.md` without a matching provider YAML file. See the [OpenAI](https://developers.openai.com/codex/skills#optional-metadata) and [Claude](https://code.claude.com/docs/en/skills) documentation.

</details>

<details>
<summary><strong>Checking disk capacity</strong></summary>

```sh
python3 skills/ds-resources/scripts/preflight.py --scratch /path/to/build-volume --project app --task parser-fix --expected-gib 20
```

Preflight checks the output directory, safe task paths, and capacity. It creates nothing and does not schedule builds. A [resource profile](examples/resource-profile.json) can select the location and headroom; pass `--scratch` only when no profile selects a root. Mounting is required unless the profile explicitly allows an ordinary directory. A command-line reserve cannot lower the profile's reserve.

</details>

## Maintain

Read [AGENTS.md](AGENTS.md). Set `TMPDIR` to an existing task-owned output directory under the project's build policy, then run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/dsstack.py doctor
```

Tests check tooling behavior. [Decision scenarios](evals/scenarios.md) check agent choices; neither establishes broad productivity gains. Keep behavioral trials selective and budgeted, as described in [validation](docs/validation.md).

---

[Design rationale](docs/focus.md) · [Sources and adaptations](docs/provenance.md) · [Source lock](upstreams.lock.json) · [License notices](licenses) · [MIT license](LICENSE)
