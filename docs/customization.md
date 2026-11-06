# Keep local policy private

The repository root holds public skills and tooling. Keep machine paths, resource limits, personal additions, and private helpers under ignored `.local/`, then assemble the needed policy into a private bundle. Agents receive concrete additions in the skill they already loaded; no separate preferences skill has to activate.

```text
.local/
  policy/
    policy.md                  # Added to every skill
    skills/
      ds-resources.md          # Added only to this skill
      ds-rust.md               # Optional domain-specific rule
    resource-profile.json      # Installed in ds-resources/profiles/default.json
  bundles/                     # Separate versioned installations
  tools/                       # Optional private helpers
  backups/                     # Private recovery material
```

Keep `policy.md` short and limited to rules that apply whenever any skill runs. Put domain-specific additions under `policy/skills/`. Use global or project instructions for policy that must apply even when no skill is selected. Additions cannot grant permissions or override host policy. Private helpers remain local; name their location in the relevant addition when an agent needs them.

For example, a private resource addition can name a build volume, a backed-up worktree directory, and what to do if the volume is missing. Its resource profile records the build volume and capacity settings:

```json
{
  "scratch": "/path/to/build-volume",
  "reserve_gib": 20,
  "warning_gib": 40,
  "require_mount": true
}
```

`require_mount: false` permits an ordinary directory. Choose values for your machine rather than copying another developer's hardware budget.

Create the policy files you need, then preview and build at a new destination:

```sh
python3 scripts/dsstack.py bundle --dest .local/bundles/v1 --local .local/policy
python3 scripts/dsstack.py bundle --dest .local/bundles/v1 --local .local/policy --apply
python3 .local/bundles/v1/scripts/dsstack.py doctor
```

An in-checkout destination must be under `.local/`, ignored by Git, and untracked. The tool checks those conditions before assembly. You may also keep inputs and bundles outside the checkout.

Review the assembled `SKILL.md` files before activating the bundle. Its preflight uses the bundled default resource profile; an explicit `--profile` selects another profile and `--scratch` supplies a root only when the profile has none.

Bundle creation leaves public source and existing installations alone. Destinations must be new; an update is another bundle followed by an explicit installation switch. Existing links into a different bundle are conflicts, so uninstall the previous bundle's owned links before installing its replacement. Keep the previous bundle for rollback and start a fresh agent session after switching.

`.local/` can contain private data, including backups of scrubbed history. Keep it untracked and avoid force-adding it. Ignoring files does not remove earlier commits; review history before a first public push.
