---
name: "ds-web"
description: "Use when changing an existing web interface, responsive layout, or browser interaction and deciding which visual or journey checks it needs."
---

# Web interface changes

- Work within the existing framework, design system, routing, and component ownership. Don't add frameworks or test runners for a local edit.
- Reproduce behavior bugs with a component or journey test at the owning boundary. Cover state that has to survive navigation, pending requests, and account switches.
- For CSS and layout, check only the states the change affects. When the request includes browser work, look at the rendered page. Check other breakpoints, focus, scrolling, or overlays only when the change touches them. DOM assertions and builds can't show what a page looks like.
- Before opening pages, find the running dev server, its port, and the login to use, then reuse them. Don't start extra servers or write to external services just to make checking easier.
- When a change touches shared routing, authentication, or several pages, run the affected end-to-end journeys once at the end.
