---
name: "ds-web"
description: "Use when changing an existing web interface, responsive layout, or browser interaction and deciding the affected visual or journey checks."
---

# Web interface changes

Work within the existing framework, design system, routing, and component ownership. Identify the user's affected task and the states that make the change observable. Use existing application scripts and browser tools; avoid introducing a second UI framework or test runner for a local edit.

For behavior changes, reproduce the failure with a focused component or journey test at the boundary that owns it. Preserve mounted state, pending requests, account context, and cleanup when changing navigation or visibility. A static screenshot cannot establish these lifecycles.

For CSS or layout changes, identify affected viewport sizes and interactions. When browser verification is in scope, completion evidence should show the rendered interface at actual relevant dimensions, including scrolling, clipping, focus, overlays, and controls touched by the change. Test nearby breakpoints when a rule changes there. DOM assertions and a successful build do not establish appearance.

Use T3 preview only when the current request asks for browser work. Loading this skill does not itself request a browser launch. When browser verification is outside the request or unavailable, state the visual or journey behavior that remains unverified.

When browser work is authorized, establish which server owns the app, its ports, and the correct authentication context before opening pages. Reuse the authoritative server where appropriate. Respect existing per-context cookies, test accounts, waiters, and write-retry rules; do not create service instances or issue external writes to simplify a check.

Run the affected journeys and required integration checks. Broader end-to-end coverage is justified by shared routing, authentication, or cross-page behavior, rather than every styling edit. Report source, visual, browser, and provider proof separately.
