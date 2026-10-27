---
name: "ds-native"
description: "Use when changing desktop or mobile application behavior that crosses packaging, operating-system permissions, or native lifecycle boundaries."
---

# Native application boundaries

Use the application's existing native framework, platform projects, build wrappers, and supported operating systems. Read its lifecycle and release conventions before changing bridges or packaging. A native task does not imply migrating to Tauri or another framework.

Place a focused behavioral regression test at the lowest boundary that owns the failure. Source and unit checks can establish state transitions, serialization, or bridge request construction. They cannot establish that the packaged application launches, receives OS callbacks, or has permission to access a device resource.

Select runtime checks from the changed boundary: packaged launch for entrypoint and asset changes; permission grant, denial, and revocation for protected resources; restart, suspend/resume, cancellation, and shutdown for lifecycle changes. Check ownership of background work and stale callbacks when windows, activities, or application sessions end. Exercise recovery paths when interrupted writes or updates can affect user data.

Use the project's isolated simulator or test-device setup when available. Keep task-owned build products, captures, symbols, and installers on Scratch through existing wrappers. Reuse valid artifacts and avoid installing additional SDKs or downloading large toolchains merely to fill a reporting gap.

Signing, entitlements, notarization, installation, and updater behavior each require their appropriate artifact or platform evidence when affected. A development launch cannot establish a signed release's permissions or update recovery. Preserve established release authorization for distribution and signing operations.

Report the exact platform, artifact, and lifecycle tested. If the host cannot exercise another supported operating system, state that platform's unverified behavior and its required gate; do not describe a source pass as cross-platform runtime acceptance.
