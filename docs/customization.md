# Keep local policy private

The public skills contain workflow and domain guidance. Put machine paths, resource limits, and personal rules outside the checkout, then assemble them into a private bundle. Agents receive the concrete additions in the skill they already loaded; no separate preferences skill has to activate.

A private directory may contain:

```text
my-dsstack/
  policy.md                    # Added to every skill
  skills/
    ds-resources.md            # Added only to this skill
    ds-rust.md                 # Optional domain-specific rule
  resource-profile.json        # Installed as profiles/default.json
```

Keep `policy.md` short and limited to rules that apply whenever any skill runs. Put domain-specific additions under `skills/`. Use global or project instructions for policy that must apply even when no skill is selected. Additions cannot grant permissions or override host policy.

For example, a private resource addition could name a build volume, a backed-up worktree directory, and what to do if the volume is missing. Its resource profile records the same build volume and capacity settings:

```json
{
  "scratch": "/path/to/build-volume",
  "reserve_gib": 20,
  "warning_gib": 40,
  "require_mount": true
}
```

`require_mount: false` permits an ordinary directory. Choose values for your machine rather than copying another developer's hardware budget.

Preview and build at a new, durable destination:

```sh
python3 scripts/dsstack.py bundle --dest ~/agent-skills/dsstack-v2 --local ~/my-dsstack
python3 scripts/dsstack.py bundle --dest ~/agent-skills/dsstack-v2 --local ~/my-dsstack --apply
python3 ~/agent-skills/dsstack-v2/scripts/dsstack.py doctor
```

Review the assembled `SKILL.md` files before activating the bundle. Its preflight uses the bundled default resource profile; an explicit `--profile` selects another profile and `--scratch` overrides the location.

Bundle creation leaves the source and any existing installation alone. Destinations must be new; an update is another bundle, followed by an explicit installation switch. Existing links into a different bundle are conflicts, so uninstall the previous bundle's owned links before installing its replacement. Keep the previous bundle to restore those links if needed.

Private inputs and assembled bundles can contain internal paths and rules. Keep them outside the public repository. `.local/` is ignored for local experimentation, but that does not remove files already committed to history. Before a first public push, review the history as well as the current tree.
