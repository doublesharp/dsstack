---
name: "ds-web"
description: "Use when changing an existing web interface, responsive layout, or browser interaction and deciding the affected visual or journey checks."
---

# Web interface changes

Use existing framework, design system, routing, component ownership, scripts, and browser tools. Identify the affected user task and observable states; avoid adding frameworks or runners for local edits.

Reproduce behavior failures with a focused component/journey test at the owning boundary. Preserve mounted state, pending requests, account context, and cleanup through navigation/visibility changes; screenshots cannot prove lifecycles.

For CSS/layout, identify affected visual states. When browser verification is authorized, inspect the rendered UI; include dimensions, scrolling, clipping, focus, overlays, and nearby breakpoints only when affected. DOM assertions/builds cannot prove appearance.

Use T3 preview only when the current request authorizes browser work under the active harness. Loading this skill grants no browser launch. State remaining visual/journey gaps when checks are unavailable or outside scope.

Before opening pages, establish the authoritative server, ports, and authentication context; reuse it where appropriate. Respect cookies per context, accounts, waiters, and write-retry rules. Do not create service instances or issue external writes to simplify checks.

Run affected journeys and required integration checks. Expand end-to-end coverage for shared routing, authentication, or cross-page changes. Report source, visual, browser, and provider evidence separately.
