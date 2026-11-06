# dsstack

Small, opinionated skills for coding agents: finish the ask, check the changed behavior, and stop. The collection covers delivery, debugging, reviews, and common application domains. Skills are plain instructions; the host supplies models, tools, and permissions.

## Start small

Start by reading [ds-work](skills/ds-work/SKILL.md), [ds-debug](skills/ds-debug/SKILL.md), [ds-tdd](skills/ds-tdd/SKILL.md), and [ds-review](skills/ds-review/SKILL.md). They define the core workflow:

- Work on one requested item at a time; record unrelated discoveries as follow-ups.
- Use focused checks while editing and run broader required checks after the edits they cover.
- Change approach after repeated failed fixes. Bound review rounds and open-ended work.
- End with what changed, what passed, and anything blocking the result.

Install the complete bundle below; some skills use shared tooling or sibling references. Agents select skills by their descriptions; explicit requests such as `Use $ds-debug to investigate this failure` also work. Project instructions and the user's task still control the work.

## Install a stable bundle

Python 3.9 or later is enough. Bundle creation and installation preview changes until `--apply` is supplied.

```sh
python3 scripts/dsstack.py bundle --dest ~/agent-skills/dsstack-v1
python3 scripts/dsstack.py bundle --dest ~/agent-skills/dsstack-v1 --apply
python3 ~/agent-skills/dsstack-v1/scripts/dsstack.py install --dest ~/.agents/skills
python3 ~/agent-skills/dsstack-v1/scripts/dsstack.py install --dest ~/.agents/skills --apply
python3 ~/agent-skills/dsstack-v1/scripts/dsstack.py doctor --dest ~/.agents/skills
```

Use the skill directory your host supports; `~/.agents/skills` and `~/.claude/skills` are common destinations. Start a fresh agent session after installation.

A bundle copies the skills and their tooling. Installed symlinks point into that bundle, so editing or updating this source checkout does not change active instructions. Keep the bundle in a durable location. The installer preserves existing directories and links owned by other installations; a conflict stops the install before changes.

For an update, build a new bundle at a new path, compare it with the active bundle, then preview uninstalling the old bundle and installing the new one. Apply those commands only when ready. Uninstall removes only that bundle's owned links; retain the old bundle for rollback. Direct installation from the source checkout is also supported for development, but makes edits live immediately.

[Customization](docs/customization.md) explains how to include private rules without publishing them. The installer does not change global instructions, model settings, plugins, or permissions.

## Skills

| Purpose | Skills |
|---|---|
| Delivery | [ds-work](skills/ds-work/SKILL.md), [ds-plan](skills/ds-plan/SKILL.md) |
| Correctness | [ds-tdd](skills/ds-tdd/SKILL.md), [ds-debug](skills/ds-debug/SKILL.md), [ds-review](skills/ds-review/SKILL.md) |
| Consultation | [ds-consult](skills/ds-consult/SKILL.md) |
| Resource use | [ds-resources](skills/ds-resources/SKILL.md) |
| Application work | [ds-rust](skills/ds-rust/SKILL.md), [ds-typescript](skills/ds-typescript/SKILL.md), [ds-web](skills/ds-web/SKILL.md), [ds-native](skills/ds-native/SKILL.md) |
| Specialized work | [ds-solidity](skills/ds-solidity/SKILL.md), [ds-ai](skills/ds-ai/SKILL.md), [ds-ux](skills/ds-ux/SKILL.md) |

Domain skills follow project toolchains and build policies. Cross-provider consultation needs the requested providers to be available. The measured UX workflow is opt-in through its task description; ordinary interface changes use ds-web.

## Resource checks

```sh
python3 scripts/dsstack.py preflight --scratch /path/to/build-volume --project app --task parser-fix --expected-gib 20
```

Preflight checks the selected output directory, safe task paths, and capacity. It creates nothing and does not schedule builds. A [resource profile](examples/resource-profile.json) can set the output location and headroom; mounting is required unless the profile explicitly allows an ordinary directory. See [customization](docs/customization.md).

## Maintain

Read [AGENTS.md](AGENTS.md) for this repository's working rules. Set `TMPDIR` to a task-owned output directory under the project's build policy, then run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/dsstack.py doctor
```

Tests check tooling behavior. [Decision scenarios](evals/scenarios.md) check the choices agents make; neither establishes broad productivity gains. [Design rationale](docs/focus.md) explains the failure patterns behind the rules. [Provenance](docs/provenance.md), the [source lock](upstreams.lock.json), and [license notices](licenses) document borrowed ideas.
