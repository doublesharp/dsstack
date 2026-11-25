# Keep local policy private

Keep machine paths, resource limits, personal instructions, and private helpers under ignored `.local/`. When you build a private bundle, dsstack appends your instructions to the relevant `SKILL.md` files.

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

Use `policy.md` for short rules shared by all bundled skills and `policy/skills/` for rules specific to one skill. Put rules that must apply in every session in global or project instructions. All additions remain subject to host policy and permissions. If an agent needs a private helper, give its path in the relevant policy file.

Use the `ds-resources` addition for worktree location and what to do if the build volume is missing. Put the build volume and capacity settings in `resource-profile.json`.

```json
{
  "scratch": "/path/to/build-volume",
  "reserve_gib": 20,
  "warning_gib": 40,
  "require_mount": true
}
```

`require_mount: false` permits an ordinary directory. Set the reserve and warning thresholds for your machine.

Create the policy files you need, then preview and build at a new destination.

```sh
python3 scripts/dsstack.py bundle --dest .local/bundles/personal-v1 --local .local/policy
python3 scripts/dsstack.py bundle --dest .local/bundles/personal-v1 --local .local/policy --apply
python3 .local/bundles/personal-v1/scripts/dsstack.py doctor
```

Keep `.local/` ignored and untracked. If it has ever been committed, review Git history for private data before publishing the repository. You can also keep policy and bundles outside the checkout.

Review the assembled `SKILL.md` files before installing. Preflight uses `ds-resources/profiles/default.json` in the bundle. Use `--profile` to select a different profile or `--scratch` to select a root when the profile leaves it unset. The bundler checks any `compute` section with the broker from tracked skill source and copies that broker and its reference into the bundle.

After review, install the bundle or switch from the active one. [Quick start](../README.md#quick-start) · [Updating an installation](../README.md#updating-an-installation)
