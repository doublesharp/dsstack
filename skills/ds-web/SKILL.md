---
name: "ds-web"
description: "Use when changing an existing web interface, responsive layout, or browser interaction and deciding which visual or journey checks it needs."
---

# Web interface changes

- Reuse the framework, design system, routing, components, and test harness. A local edit doesn't need new frameworks or runners.
- Cover state that must survive navigation, pending requests, and account switches at the owning component or journey boundary.
- For CSS and layout, inspect affected states, breakpoints, focus, scrolling, and overlays. When browser work is requested, inspect the rendered page; DOM assertions and builds don't show appearance.
- Write visible text for product users. Put internal status, test notes, and unfinished-work caveats in the handoff, not labels, errors, or marketing copy, unless requested.
- Reuse the running dev server, port, and login. Don't start extra servers or write to external services just to simplify checking.
- Include affected end-to-end journeys when a change touches shared routing, authentication, or several pages.
