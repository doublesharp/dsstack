---
name: "ds-native"
description: "Use when changing desktop or mobile application behavior that crosses packaging, operating-system permissions, or native lifecycle boundaries."
---

# Native application changes

- Reuse the native framework, platform projects, wrappers, and supported OS versions. Consolidate repeated UI the change touches into shared components and platform theme resources; keep intentional variants and unrelated screens unchanged.
- Test at the boundary that owns the behavior: unit tests for state, serialization, and bridge calls; the running app for launch, OS callbacks, and permissions.
- Pick runtime checks by what changed: packaged launch for entrypoints and assets; grant, deny, and revoke for permissions; restart, suspend and resume, and shutdown for lifecycle; an interrupted write for stored user data.
- Reuse configured simulators, devices, output locations, and matching artifacts. Use available sccache for Rust/C/C++ builds through existing wrappers; for CMake, set `CMAKE_C_COMPILER_LAUNCHER` and `CMAKE_CXX_COMPILER_LAUNCHER` to `sccache`. Report an unavailable platform instead of installing a large toolchain just to add a check.
- Signing, entitlements, notarization, installers, and updaters need a signed artifact to check. A development launch can't show them.

Close unused task-started processes or simulators and remove task-only builds and captures; preserve shared devices and requested installers.
