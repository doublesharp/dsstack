# Sources and adaptations

Exact upstream revisions and file hashes are in [upstreams.lock.json](../upstreams.lock.json), and upstream MIT notices are in [licenses](../licenses). dsstack installs no upstream code or hooks.

## Adapted workflows

| Source | Idea | How dsstack differs |
|---|---|---|
| t3dotgg/tstack sol-loop and council | Bounded review, one reviewer by default, independent named reviewers on request | Two rounds by default, must-fix versus follow-up, no agreement loop or brand requirement |
| t3dotgg/tstack full-stop | Owning work through to a clear finish | No activation by emphatic phrases, and the user's authority stays binding |
| obra/superpowers TDD and debugging | Failing test first, root-cause hypotheses | No test per helper, no workspace rerun after every step, no revert-to-red cycle |
| obra/superpowers brainstorming and writing-plans | Intent discovery, buildable specs, task decomposition | One planning skill sized to the work, no compulsory spec, plan, and review sequence |
| Existing project contracts | Scratch routing and domain test boundaries | Project commands, versions, trackers, and required checks still win |

The consultation route also draws on the local `claude-code` skill's read-only handoff and completion rules. Its hash is under `local_sources` in the lock. Codex syntax was checked against the installed `codex exec --help`.

## Published guidance for the 2026-10-31 revision

All pages were read on 2026-10-31. Quotes are short excerpts, and the skills paraphrase rather than copy.

Anthropic

- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5). Verification instructions "cause over-verification on Claude Opus 5, and removing them reduces wasted tokens with no loss in quality."
- [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5). "Stop after two or three automatic continuations on the same task rather than repeating them indefinitely."
- [Prompting Claude Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5). "Don't start extra rounds of review or hardening on your own."
- [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1). For work found mid-task, "don't fix, optimize or extend it in this change."
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices). "A reviewer that's asked to find problems will always find something." After two failed corrections, start fresh.
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), 2025-11-26. "Work on only one feature at a time."
- [Building a C compiler](https://www.anthropic.com/engineering/building-c-compiler), 2026-02-05. Claude "will happily spend hours running tests instead of making progress."

OpenAI

- [Using GPT-6 Astra](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra). "Broaden or repeat testing only when new changes, failures, or unresolved concerns justify it."
- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), 2026-09-11. Instructions written for older models "can lead to unnecessary testing."
- [GPT-5.6 prompt guidance](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6). "Use ALWAYS, NEVER, must, and only for true invariants."
- [Codex prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide), 2026-02-25. "If you find yourself re-reading or re-editing the same files without clear progress, stop."
- [Harness engineering](https://openai.com/index/harness-engineering/), 2026-02-11. "Give Codex a map, not a 1,000-page instruction manual."

Practitioners and research

- Geoffrey Huntley, [Ralph](https://ghuntley.com/ralph/), 2025-07-14. "Ask Ralph to do one thing per loop."
- Steve Yegge, [Beads](https://github.com/steveyegge/beads). Agents file newly discovered work as issues, and sessions end by "landing the plane."
- Kent Beck, [Augmented coding: beyond the vibes](https://tidyfirst.substack.com/p/augmented-coding-beyond-the-vibes), 2025-06-25. He steps in on loops, unrequested functionality, and disabled or deleted tests.
- HumanLayer, [12-factor agents, factor 9](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md). About three attempts at a tool before escalating.
- Mitchell Hashimoto, [My AI adoption journey](https://mitchellh.com/writing/my-ai-adoption-journey), 2026-02-05. Each AGENTS.md line answers a real agent failure.
- Armin Ronacher, [Agentic coding recommendations](https://lucumr.pocoo.org/2025/6/12/agentic-coding/), 2025-06-12. "Crashes are tolerable; hangs are problematic."
- Cemri et al., [Why do multi-agent LLM systems fail?](https://arxiv.org/abs/2503.13657). Step repetition and unawareness of termination conditions are among the most common failures.
- [ImpossibleBench](https://arxiv.org/abs/2510.20270). Agents "may delete failing tests rather than fix the underlying bug."

## Updating

The 2026-11-03 [UX skill proposal](ux-proposal.md) records its local Claude and Codex session sources and the incorporated Opus 5.5 review. Its rubric condenses the user's prompts; the later six-round council instruction sets the workflow. [Competition-loop research](ux-loop-research.md) records the primary papers, adapted ideas, and limits.

Compare a pinned source's new revision file by file, and keep or revise each adaptation on purpose. Stars and activity don't show that agents finish more work. Don't merge upstream automatically or bring back model-specific instructions that newer guidance retired.
