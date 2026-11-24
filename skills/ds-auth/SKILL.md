---
name: "ds-auth"
description: "Use when designing a new application's accounts or implementing or changing login, passkeys, MFA, account recovery, sessions, identity linking, or delegated API/CLI/MCP access. Also use for authorization changes that depend on authentication strength; ordinary role or resource-permission edits alone do not need this skill."
---

# Design authentication around the authority it grants

Read [the auth policy](references/policy.md) before choosing or changing authentication behavior. It defines the shared defaults; the application chooses its provider and identity store. Preserve the user's requirements and existing product boundaries. A local application may need no account.

1. Inspect existing login, enrollment, recovery, sessions, permissions, and agent access. Identify which actions expose personal data, move money, change credentials, or grant administrative authority. Select the relevant policy profiles and reuse the existing auth framework. Refresh provider documentation before relying on supported features or defaults.
2. For a new app, record the selected profiles, trusted origins/RP ID, factors, session limits, recovery transition and promotion rules, and provider in its existing architecture docs. For an existing app, update that record only where this task changes it. State deliberate exceptions and their consequences. Keep scope to the requested behavior.
3. Default ordinary online accounts to passkeys with required user verification. Protect privileged control-plane access with independent hardware keys. Keep authentication method, credential enrollment provenance, verification time, and recovery restrictions in server-controlled state. Enforce sensitive-action requirements alongside current resource permissions in the application operation shared by HTTP, CLI, and MCP.
4. Treat account recovery as a restricted state transition. Define the proof needed to restore each capability before implementing factor replacement. A newly enrolled passkey inherits recovery restrictions until an independent promotion rule succeeds. Keep local vault decryption recovery separate from account access.
5. Deliver the whole affected user journey: clear sign-in choices, factor enrollment and removal, independent backup setup, recovery, and session/grant revocation. Preserve working login methods during migration until the replacement and its recovery path have been verified. Use generic public errors and bounded attempts; keep useful failure detail in redacted operational logs.
6. Select checks by the changed boundary. Cover replayed/expired challenges, unverified WebAuthn responses, recovery-to-privilege escalation, stale or revoked sessions/grants, and cross-account access where affected. Verify platform acceptance on supported devices. Run project-required checks once after edits, report unavailable device/provider checks, and stop when the requested change is complete.

Use the [decision scenarios](references/scenarios.md) to review difficult choices. Keep applications independent unless federation is selected; migrate only projects in scope.
