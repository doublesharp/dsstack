# Sources and adaptations

Exact upstream revisions and file hashes are in [upstreams.lock.json](../upstreams.lock.json), and upstream MIT notices are in [licenses](../licenses). dsstack installs no upstream code or hooks.

## Adapted workflows

| Source | Idea | How dsstack differs |
|---|---|---|
| t3dotgg/tstack sol-loop and council | Bounded review, one reviewer by default, independent named reviewers on request | Two rounds by default, must-fix versus follow-up, no agreement loop or brand requirement |
| t3dotgg/tstack full-stop | Owning work through to a clear finish | No activation by emphatic phrases, and the user's authority stays binding |
| obra/superpowers TDD and debugging | Failing test first, root-cause hypotheses | No test per helper, no workspace rerun after every step, no revert-to-red cycle |
| obra/superpowers brainstorming and writing-plans | Intent discovery, buildable specs, task decomposition | One planning skill sized to the work, no compulsory spec, plan, and review sequence |
| Existing project contracts | Output routing and domain test boundaries | Project commands, versions, trackers, and required checks still win |

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

## Compact, independent skills, 2026-11-06

The source lock pins the compared files; instructions are paraphrased and upstream code is not executed.

- [pstack TDD](https://github.com/cursor/plugins/blob/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack/skills/tdd/SKILL.md): choose a useful executable regression check when a new harness would outgrow the change; project-required checks remain binding.
- [pstack interrogate](https://github.com/cursor/plugins/blob/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack/skills/interrogate/SKILL.md): substantiate findings. Here, a complete source trace can establish a defect when running it is impractical; no adversary fan-out is required.
- [pstack idempotency](https://github.com/cursor/plugins/blob/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack/skills/principle-make-operations-idempotent/SKILL.md): cover repeated delivery and interrupted side effects where the same operation can be retried.
- [Anthropic skill creator](https://github.com/anthropics/skills/blob/ca45fc496a3436251f191354091d557da31c15b5/skills/skill-creator/SKILL.md) and [Superpowers writing-skills](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/writing-skills/SKILL.md): compare affected behavior with the prior skill. Trials stay selective and budgeted, without a mandatory viewer or benchmark pipeline.
- [tstack takeover](https://github.com/t3dotgg/tstack/tree/main/skills/takeover): treat inherited completion claims as context. Reuse valid results and check only an unsupported dependency the next item needs.

General councils belong to ds-consult; UX scoring and round accounting belong to ds-ux. Each skill keeps its own references and essential procedure. A fuzzy checker for repeated prose was declined: self-contained skills can use different wording, and scenario declarations test a useful structural boundary instead.

## Writing guidance, 2026-11-06

The ds-write instructions are written independently after comparing the current [pstack unslop](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md), [Humanizer 3.1.0](https://github.com/blader/humanizer/blob/main/SKILL.md), [theclaymethod unslop 2.3.0](https://github.com/theclaymethod/unslop/blob/main/references/core-contract.md), [ccf humanize](https://github.com/ccf/humanize/blob/main/skills/humanize/references/principles.md), and [mshumer unslop](https://github.com/mshumer/unslop). These links record the consulted sources; version labels were read from the served files, not verified against commit hashes.

The skill uses a short drafting/editing procedure with fact and voice preservation. It imports no pattern catalog, scanner, scoring system, or upstream skill text. Personal voice preferences belong in local policy. The evaluation includes legitimate punctuation and lists that should survive editing.

## Compiler caching, 2026-11-06

- [sccache usage and supported compilers](https://github.com/mozilla/sccache#usage): use compiler wrappers or CMake launchers for supported Rust, C/C++, and CUDA/HIP builds; inspect cache statistics when configuring or diagnosing reuse.
- [sccache Rust support](https://github.com/mozilla/sccache/blob/main/docs/Rust.md): incremental rustc output is not cacheable. Keep warm Cargo targets and stable compiler settings rather than forcing cold builds to demonstrate cache hits.
- [sccache compiler dispatch](https://github.com/mozilla/sccache/blob/main/src/compiler/compiler.rs) does not natively wrap solc/Solar. The [forgeds runtime adapter](https://github.com/doublesharp/foundry/blob/812bfab1f3d2bb5fb969fd8bfcbeb0fd76b7bc84/docs/dev/solidity-compiler-cache.md) keeps the shared local Solidity-result cache first and optionally uses sccache 0.19.0 raw storage over TCP. Its trace events establish hits; ordinary sccache compiler counters do not record these operations.
- Prefer the project's pinned [prebuilt forgeds release](https://github.com/doublesharp/foundry/releases/tag/forgeds), checking SHA-256 and full commit identity; retain Cargo source builds when a platform has no matching asset. The selected toolchain is `forgeds` from [doublesharp/foundry](https://github.com/doublesharp/foundry) with [Solar](https://github.com/paradigmxyz/solar#binary-usage) for compatible development work. [Cargo install](https://doc.rust-lang.org/cargo/commands/cargo-install.html) supports pinned Git revisions, binary selection, required features, and reusable build output. Select a fork revision whose manifest provides `forgeds`; retain the project's wrappers, artifact paths, and approved release compiler.

## cargo-steward, 2026-11-07

On machines with cargo-steward, ds-rust's sccache rule told agents to set `RUSTC_WRAPPER=sccache`, which bypasses cargo-steward's rustc wrapper; its separate-target and manual-cleanup rules duplicated what the `cargo` proxy and `cargo steward remove --worktree` already do under Cargo's locks. ds-rust now detects the tool, keeps the earlier rules for machines without it, and defers details to the `cargo-steward` skill that the tool installs (`cargo steward skill install`).

## Worktree startup, 2026-11-06

The reported failure was: “The dev startup hit a dependency-link issue in the new worktree; I’m correcting the launch path before taking baseline captures.” It does not identify the package manager or exact error. General setup and working-directory checks belong to ds-work; Node dependency-link inspection and repair belong to ds-typescript. ds-web and ds-ux confirm the served checkout before captures. The decision scenarios cover each boundary, preserving the two-attempt environment repair limit.

## Updating

The UX rubric, six-round budget, and alternating-provider workflow are author choices maintained in the skill's own references.

Compare a pinned source's new revision file by file, and keep or revise each adaptation on purpose. Stars and activity don't show that agents finish more work. Don't merge upstream automatically or bring back model-specific instructions that newer guidance retired.
