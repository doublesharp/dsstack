---
name: "ds-plan"
description: "Use when the user asks for a spec or plan, or when a feature request is unclear enough that building the wrong thing is the main risk."
---

# Plan only as much as the work needs

Small, clear tasks need no plan. Start with the ds-work checklist instead.

1. Read the relevant code, docs, and any existing spec or plan first. Reuse what is good enough.
2. Ask only questions whose answers change what gets built and that the repo can't answer. For everything else, pick a reasonable default and label it an assumption.
3. For a design choice that is expensive to reverse, give two or three options with their trade-offs and recommend one.
4. Describe what to build: the behavior, the failure cases that matter, the interfaces and data other parts depend on, and what is out of scope. Leave routine implementation choices to whoever builds it.
5. Break the work into deliverable items in dependency order. Each item names its files, its done-when check, and whether it can run in parallel. Schedule slow or broad checks once at the end instead of after every item.

A small feature needs a few lines. A multi-week project needs a document. Save it where the project keeps plans or specs, or in its tracker. A plan-only request ends with the plan. Otherwise carry it out with ds-work without asking for approval again.
