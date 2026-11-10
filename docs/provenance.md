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

## Direct claims and useful qualifications

The reported failure was repeated caveats about what a product or claim does not do, plus unnecessary dates. The ds-write revision replaces its broad caveat advice with a reader-misunderstanding test, a deletion check inside the existing revision, and a short positive example. It retains uncertainty, operational conditions, deadlines, and dates that determine whether a fact is true.

- [Anthropic's prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#control-the-format-of-responses): describe the desired output and use relevant examples. The skill leads with direct, supported descriptions and follows supplied voice samples.
- [Ian Quah's writing guide, sections 4, 11, and 15](https://ianq.ai/personal_notes/signs_of_ai_writing/): test whether a contrast excludes a plausible reading; inspect paragraph structure for repeated qualifications that survive phrase replacement. The final meaning check covers contrasts split across sentences and disguised as comma tails.
- [Conor Bronsdon's avoid-ai-writing, Narrated candor](https://github.com/conorbronsdon/avoid-ai-writing/blob/main/dist/avoid-ai-writing.md#narrated-candor), served version 3.38.0: remove disclosure announcements when the information survives their deletion. Its phrase detector for this pattern was reverted because it also matched useful disclosures. The skill uses contextual judgment instead of a scanner.
- [blader/humanizer, sections 23 and 25](https://github.com/blader/humanizer/blob/main/SKILL.md), served version 4.0.0: remove knowledge-limit residue and repeated document narration while preserving meaning. The skill distinguishes routine freshness stamps from dates needed by the reader.
- [Practitioner discussion of repeated caveats](https://www.reddit.com/r/vibecoding/comments/1xmn5y4/codexgpt_and_the_endless_caveats/): kenthesaint reports using positive samples and a separate editing pass; CleanFix_Dev suggests phrase checks and more concrete source facts. ds-write uses a sample and the existing meaning check, keeping a single-writer workflow. Required limitations stay with the relevant claim instead of moving to a blanket footer.
- [Alex Bleakley's negated-instruction experiments](https://alexbleakley.com/blog/saying-what-not-to-do): positive and negative instructions performed similarly on some tested tasks. These older-model results support testing the actual writing task, not a universal claim that negative instructions fail.

These sources informed independently written instructions and an illustrative example; no upstream implementation or pattern catalog is included. The decision scenarios cover redundant scope statements, necessary conditions and dates, source fidelity, and supplied voice.

## Compiler caching, 2026-11-06

- [sccache usage and supported compilers](https://github.com/mozilla/sccache#usage): use compiler wrappers or CMake launchers for supported Rust, C/C++, and CUDA/HIP builds; inspect cache statistics when configuring or diagnosing reuse.
- [sccache Rust support](https://github.com/mozilla/sccache/blob/main/docs/Rust.md): incremental rustc output is not cacheable. Keep warm Cargo targets and stable compiler settings rather than forcing cold builds to demonstrate cache hits.
- [sccache compiler dispatch](https://github.com/mozilla/sccache/blob/main/src/compiler/compiler.rs) does not natively wrap solc/Solar. The [forgeds runtime adapter](https://github.com/doublesharp/foundry/blob/812bfab1f3d2bb5fb969fd8bfcbeb0fd76b7bc84/docs/dev/solidity-compiler-cache.md) keeps the shared local Solidity-result cache first and optionally uses sccache 0.19.0 raw storage over TCP. Its trace events establish hits; ordinary sccache compiler counters do not record these operations.
- Prefer the project's pinned [prebuilt forgeds release](https://github.com/doublesharp/foundry/releases/tag/forgeds), checking SHA-256 and full commit identity; retain Cargo source builds when a platform has no matching asset. The selected toolchain is `forgeds` from [doublesharp/foundry](https://github.com/doublesharp/foundry) with [Solar](https://github.com/paradigmxyz/solar#binary-usage) for compatible development work. [Cargo install](https://doc.rust-lang.org/cargo/commands/cargo-install.html) supports pinned Git revisions, binary selection, required features, and reusable build output. Select a fork revision whose manifest provides `forgeds`; retain the project's wrappers, artifact paths, and approved release compiler.

## forgeds agent workflows, 2026-11-08

The missing guidance was changed-only warnings, reusable instrumented coverage, compact coverage gaps, and CI cache reuse. The fork's [feature guide](https://github.com/doublesharp/foundry/blob/402b5f166132929d556f431dd3d8f9ccb698e99d/FORGEDS.md) now makes these discoverable from its README. Instructions are paraphrased from that guide and checked against the implementation and tests at `4ca15fcba25aa61a1b436d28b428e30b459f3d56`:

- [Compiler warning configuration](https://github.com/doublesharp/foundry/blob/4ca15fcba25aa61a1b436d28b428e30b459f3d56/crates/config/src/lib.rs) and [build tests](https://github.com/doublesharp/foundry/blob/4ca15fcba25aa61a1b436d28b428e30b459f3d56/crates/forge/tests/cli/build.rs) establish `compiler_warnings = "changed"`, profile inheritance, and visibility of errors and denied warnings.
- [Coverage command](https://github.com/doublesharp/foundry/blob/4ca15fcba25aa61a1b436d28b428e30b459f3d56/crates/forge/src/cmd/coverage.rs) and [coverage tests](https://github.com/doublesharp/foundry/blob/4ca15fcba25aa61a1b436d28b428e30b459f3d56/crates/forge/tests/cli/coverage.rs) establish compiler-output reuse with solc and Solar, fresh execution and coverage metadata on reruns, and `--report gaps` with `--report-file`. Instrumentation retains optimizer/viaIR settings but changes bytecode and gas.
- [Shared compiler caching](https://github.com/doublesharp/foundry/blob/4ca15fcba25aa61a1b436d28b428e30b459f3d56/docs/dev/solidity-compiler-cache.md) defines stable compiler inputs, local locking, and optional sccache storage for CI. Shared compiler results and project caches serve different purposes; preserve both.

The skill keeps the project's approved release compiler and required coverage modes. It makes no timing claim and imports no upstream code.

## cargo-steward, 2026-11-07

On machines with cargo-steward, ds-rust's sccache rule told agents to set `RUSTC_WRAPPER=sccache`, which bypasses cargo-steward's rustc wrapper; its separate-target and manual-cleanup rules duplicated what the `cargo` proxy and `cargo steward remove --worktree` already do under Cargo's locks. ds-rust now detects the tool, keeps the earlier rules for machines without it, and defers details to the `cargo-steward` skill that the tool installs (`cargo steward skill install`).

## Worktree startup, 2026-11-06

The reported failure was: “The dev startup hit a dependency-link issue in the new worktree; I’m correcting the launch path before taking baseline captures.” It does not identify the package manager or exact error. General setup and working-directory checks belong to ds-work; Node dependency-link inspection and repair belong to ds-typescript. ds-web and ds-ux confirm the served checkout before captures. The decision scenarios cover each boundary, preserving the two-attempt environment repair limit.

## Optional security review, 2026-11-08

`ds-security` adapts the source-grounded finding discipline and supply-chain trust questions from [Cloudflare's security-audit-skill](https://github.com/cloudflare/security-audit-skill/tree/d24bc269171a9171fac58493e0ffba511d571a4a), especially its [entrypoint](https://github.com/cloudflare/security-audit-skill/blob/d24bc269171a9171fac58493e0ffba511d571a4a/skills/security-audit/SKILL.md) and [supply-chain companion](https://github.com/cloudflare/security-audit-skill/blob/d24bc269171a9171fac58493e0ffba511d571a4a/skills/security-audit/SUPPLY-CHAIN-AND-RELEASE.md). Exact consulted file hashes are in the source lock. The installed local copy was inspected to diagnose the reported failure; no instruction text was copied from it.

The MIT license is retained in [licenses/security-audit-LICENSE](../licenses/security-audit-LICENSE) and inside the standalone skill. The new instructions are written for dsstack: opt-in installation, ordinary project checks for dependency patches, containment chosen for hazardous execution, findings supported by source or execution, and bounded reviews without mandatory agents, ledgers, or report files. No upstream code or validators are imported. The triggering failure was a routine dependency patch that skipped all builds/tests because macOS could not enforce every audit-only memory control.

## Updating

The UX rubric, six-round budget, and alternating-provider workflow are author choices maintained in the skill's own references.

Compare a pinned source's new revision file by file, and keep or revise each adaptation on purpose. Stars and activity don't show that agents finish more work. Don't merge upstream automatically or bring back model-specific instructions that newer guidance retired.
