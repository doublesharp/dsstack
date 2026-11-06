---
name: "ds-native"
description: "Use when changing desktop or mobile application behavior that crosses packaging, operating-system permissions, or native lifecycle boundaries."
---

# Native application changes

- Use the existing native framework, platform projects, wrappers, and supported OS versions. Native work doesn't call for a framework migration.
- Test at the lowest boundary that owns the behavior. Unit tests cover state, serialization, and bridge calls. Launch, OS callbacks, and permissions need the running app.
- Pick runtime checks by what changed: packaged launch for entrypoints and assets; grant, deny, and revoke for permissions; restart, suspend and resume, and shutdown for lifecycle; an interrupted write for stored user data.
- Use the project's simulators, test devices, and output locations. Reuse artifacts that still match the source.
- Don't install SDKs or large toolchains just to add a check. Name the platform you couldn't run instead.
- Signing, entitlements, notarization, installers, and updaters need a signed artifact to check. A development launch can't show them.
