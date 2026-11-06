# Optional always-on block

Skills load only when a description matches the task, so the core rules can miss small or oddly worded requests. This block carries them into every session. dsstack doesn't apply it.

To adopt it, add the block to your host's global instructions file, such as `~/.codex/AGENTS.md` or `~/.claude/CLAUDE.md`. Check which file your host actually loads. Replace older workflow paragraphs that say the same thing rather than keeping both.

```markdown
# Working style

- When the user's instructions conflict with a skill or a memory, follow the user.
- Finish one requested item at a time, and record unrelated discoveries as follow-ups.
- For open-ended asks like "make it faster", state a metric, a target, and a budget first, and stop at the target or the budget.
- Use focused checks while editing. Run slow checks once, after the edits they cover, and reuse passes that later edits didn't touch.
- Run the checks the project requires. Commits and a short handoff are the record, so create receipts, manifests, or evidence packets only when the user or project asks.
- After one or two direct fixes for an environment problem, report it as a blocker instead of working around it.
- Report results in plain words: what ran, what passed, and what didn't run. Don't label work "qualified" or "unqualified".
- Add a caveat only when it changes what the reader should do. Keep internal status, test notes, and hedges out of product copy, UI text, and user-facing docs.
- Once the requested result and required checks are done, hand off in a few lines and stop.
```
