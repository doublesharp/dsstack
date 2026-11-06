---
name: "ds-web"
description: "Use when changing an existing web interface, responsive layout, or browser interaction and deciding which visual or journey checks it needs."
---

# Web interface changes

- Work within the existing framework, design system, routing, and component ownership. Don't add frameworks or test runners for a local edit.
- Cover state that must survive navigation, pending requests, and account switches at the owning component or journey boundary.
- For CSS and layout, check only the states, breakpoints, focus, scrolling, or overlays the change touches. When the request includes browser work, look at the rendered page. DOM assertions and builds can't show what a page looks like.
- Write visible text for the product's users. Keep internal status, test notes, hedges, and caveats about unfinished work out of labels, empty states, errors, and marketing copy unless the user asks for them, and put them in the handoff instead.
- Before opening pages, find the running dev server, its port, and the login to use, then reuse them. Don't start extra servers or write to external services just to make checking easier.
- Include affected end-to-end journeys when a change touches shared routing, authentication, or several pages.
