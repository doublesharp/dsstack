---
name: "ds-native"
description: "Use when changing desktop or mobile application behavior that crosses packaging, operating-system permissions, or native lifecycle boundaries."
---

# Native application boundaries

Use existing native frameworks, platform projects, wrappers, supported operating systems, and lifecycle/release conventions. Native work does not imply a framework migration.

Put focused behavioral regressions at the lowest owning boundary. Source/unit checks can establish state transitions, serialization, or bridge requests; packaged launch, OS callbacks, and device permissions need runtime evidence.

Select checks by affected boundary: packaged launch for entrypoints/assets; permission grant, denial, and revocation for protected resources; restart, suspend/resume, cancellation, and shutdown for lifecycle changes. Check background-work ownership and stale callbacks as windows, activities, or sessions end. Exercise recovery when interrupted writes/updates can affect user data.

Use isolated project simulators/test devices when available. Keep builds, captures, symbols, and installers on Scratch through existing wrappers; reuse valid artifacts. Do not install SDKs or large toolchains merely to fill evidence gaps.

Signing, entitlements, notarization, installation, and updater changes need appropriate artifact/platform evidence. Development launch cannot prove signed-release permissions or update recovery. Preserve distribution/signing authorization.

Report exact platform, artifact, and lifecycle tested. For supported systems unavailable on the host, state unverified behavior and required gates; source passes cannot establish cross-platform runtime acceptance.
