# Trying the skills safely

Build a bundle at a new path and install it into an empty, task-specific skill directory first. Run doctor against that destination and try a small request with the appropriate host configuration.

Observe whether the agent finishes the requested outcome, chooses checks that cover its edits, respects project instructions, and stops at completion. [Decision scenarios](../evals/scenarios.md) offer bounded requests that require no live services.

Before switching an existing installation, record its skill sources and preserve the configuration needed to restore them. The installer reports conflicting directories and foreign links instead of replacing them. Disabling other workflow packs or editing global instructions is a separate, explicit choice.

After switching, start a fresh session. To roll back a bundle installation, uninstall its owned links and reinstall the previous bundle. Keep private configuration, archives, and session records outside the public repository.

See [customization](customization.md) for local policy and [validation](validation.md) for tooling checks.
