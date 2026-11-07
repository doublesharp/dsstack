---
name: "ds-web"
description: "Use when changing an existing web interface, responsive layout, or browser interaction and deciding which visual or journey checks it needs."
---

# Web interface changes

- Reuse the framework, design system, routing, components, and test harness; a local edit needs no new framework or runner. Use CSS or the project's styling system with theme tokens and variants instead of repeated style literals or copied inline styles. Move UI repeated across call sites in scope into shared components; keep intentional variants and unrelated code unchanged. Check shared style changes in each affected component and supported theme.
- Cover state that must survive navigation, pending requests, and account switches at the owning component or journey boundary.
- For CSS and layout, inspect affected states, breakpoints, focus, scrolling, and overlays. When browser work is requested, inspect the rendered page; DOM assertions and builds don't show appearance.
- Write visible text for product users. Put internal status, test notes, and unfinished-work caveats in the handoff, not labels, errors, or marketing copy, unless requested.
- Reuse the running dev server, port, and login after confirming it serves the intended checkout and requested route. Don't start extra servers or write to external services just to simplify checking.
- Include affected end-to-end journeys when a change touches shared routing, authentication, or several pages.
