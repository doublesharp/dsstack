# Sources and adaptations

dsstack ships its own skill text and tooling. The source lock records revisions and file hashes for pinned material, and the license directory holds the upstream MIT notices. [Source lock](../upstreams.lock.json) · [License notices](../licenses)

## Adapted workflows

| Source | Idea | How dsstack differs |
|---|---|---|
| t3dotgg/tstack sol-loop and council | Independent reviews, cross-provider councils, and findings checked as they arrive | Task-specific roster and reasoning effort, direct handling of small tasks, and bounded rechecks |
| t3dotgg/tstack full-stop | Owning work through to a clear finish | The task and the user's authorization determine the finish line |
| obra/superpowers TDD and debugging | Failing test first, root-cause hypotheses | Tests at behavior boundaries and focused reruns during edits |
| obra/superpowers brainstorming and writing-plans | Intent discovery, buildable specs, and task decomposition | One planning skill sized to the work |
| Existing project contracts | Output routing and domain test boundaries | Project commands, versions, trackers, and required checks still win |

## Published guidance for the 2026-10-31 revision

The skills paraphrase guidance from the sources consulted for this revision.

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

The source lock pins the compared files.

- [pstack TDD](https://github.com/cursor/plugins/blob/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack/skills/tdd/SKILL.md): choose a useful executable regression check when a new harness would outgrow the change; project-required checks remain binding.
- [pstack interrogate](https://github.com/cursor/plugins/blob/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack/skills/interrogate/SKILL.md): substantiate findings. Here, a complete source trace can establish a defect when running it is impractical; no adversary fan-out is required.
- [pstack idempotency](https://github.com/cursor/plugins/blob/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack/skills/principle-make-operations-idempotent/SKILL.md): cover repeated delivery and interrupted side effects where the same operation can be retried.
- [Anthropic skill creator](https://github.com/anthropics/skills/blob/ca45fc496a3436251f191354091d557da31c15b5/skills/skill-creator/SKILL.md) and [Superpowers writing-skills](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/writing-skills/SKILL.md): compare affected behavior with the prior skill. Trials stay selective and budgeted, without a mandatory viewer or benchmark pipeline.
- [tstack takeover](https://github.com/t3dotgg/tstack/tree/main/skills/takeover): treat inherited completion claims as context. Reuse valid results and check only an unsupported dependency the next item needs.

`ds-consult` defines general councils, and `ds-ux` defines UX scoring and round budgets. Each skill includes the references and procedure it needs. The scenario declarations let `doctor` check which skills each scenario names.

## Writing guidance, 2026-11-06

`ds-write` sets out a short editing procedure that preserves facts and the author's voice. It was written independently after comparing the sources below. Version labels are from the files as served. [pstack unslop](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md) · [Humanizer 3.1.0](https://github.com/blader/humanizer/blob/main/SKILL.md) · [theclaymethod unslop 2.3.0](https://github.com/theclaymethod/unslop/blob/main/references/core-contract.md) · [ccf humanize](https://github.com/ccf/humanize/blob/main/skills/humanize/references/principles.md) · [mshumer unslop](https://github.com/mshumer/unslop)

The scenarios check that edits preserve deliberate punctuation and lists. Put personal voice preferences in local policy.

## Direct claims and useful qualifications

Repeated caveats and unnecessary dates prompted a revision to `ds-write`. The skill asks writers to try deleting each qualification during the edit and keep it when deletion changes the meaning, confidence, or reader's next action. That includes uncertainty, operational conditions, deadlines, and dates that determine whether a fact is true.

- [Anthropic's prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#control-the-format-of-responses): describe the desired output and use relevant examples. The skill leads with direct, supported descriptions and follows supplied voice samples.
- [Ian Quah's writing guide, sections 4, 11, and 15](https://ianq.ai/personal_notes/signs_of_ai_writing/): test whether a contrast excludes a plausible reading; inspect paragraph structure for repeated qualifications that survive phrase replacement. The final meaning check covers contrasts split across sentences and disguised as comma tails.
- Remove disclosure announcements when the information survives their deletion. A phrase detector for this pattern also matched useful disclosures, so the project reverted it. [Conor Bronsdon's avoid-ai-writing, Narrated candor, served version 3.38.0](https://github.com/conorbronsdon/avoid-ai-writing/blob/main/dist/avoid-ai-writing.md#narrated-candor)
- [blader/humanizer, sections 23 and 25](https://github.com/blader/humanizer/blob/main/SKILL.md), served version 4.0.0: remove knowledge-limit residue and repeated document narration while preserving meaning. The skill distinguishes routine freshness stamps from dates needed by the reader.
- [Practitioner discussion of repeated caveats](https://www.reddit.com/r/vibecoding/comments/1xmn5y4/codexgpt_and_the_endless_caveats/): kenthesaint reports using positive samples and a separate editing pass; CleanFix_Dev suggests phrase checks and more concrete source facts. ds-write uses a sample and the existing meaning check, keeping a single-writer workflow. Required limitations stay with the relevant claim instead of moving to a blanket footer.
- Positive and negative instructions performed similarly on some tasks with the models tested. Evaluate the instructions on the writing task you care about. [Alex Bleakley's negated-instruction experiments](https://alexbleakley.com/blog/saying-what-not-to-do)

The decision scenarios cover redundant scope statements, necessary conditions and dates, source fidelity, and supplied voice.

The light-edit trial drew on [Weston Hancock's Unslop eval](https://github.com/westonhancock/unslop/blob/main/eval.md#voice-do-these-checks-first) for preserving strong original sentences and [Sepia's discourse guidance](https://github.com/Nanako0129/sepia/blob/v0.13.0/skills/sepia/references/discourse-pass.md) for checking what each section contributes. The ds-write scenario checks an unchanged passage and a procedure whose steps belong together.

## Compiler caching, 2026-11-06

- [sccache usage and supported compilers](https://github.com/mozilla/sccache#usage): use compiler wrappers or CMake launchers for supported Rust, C/C++, and CUDA/HIP builds; inspect cache statistics when configuring or diagnosing reuse.
- [sccache Rust support](https://github.com/mozilla/sccache/blob/main/docs/Rust.md): incremental rustc output is not cacheable. Keep warm Cargo targets and stable compiler settings rather than forcing cold builds to demonstrate cache hits.
- [sccache compiler dispatch](https://github.com/mozilla/sccache/blob/main/src/compiler/compiler.rs) does not natively wrap solc/Solar. The [forgeds runtime adapter](https://github.com/doublesharp/foundry/blob/812bfab1f3d2bb5fb969fd8bfcbeb0fd76b7bc84/docs/dev/solidity-compiler-cache.md) keeps the shared local Solidity-result cache first and optionally uses sccache 0.19.0 raw storage over TCP. Its trace events establish hits; ordinary sccache compiler counters do not record these operations.
- Prefer the project's pinned [prebuilt forgeds release](https://github.com/doublesharp/foundry/releases/tag/forgeds), checking SHA-256 and full commit identity; retain Cargo source builds when a platform has no matching asset. The selected toolchain is `forgeds` from [doublesharp/foundry](https://github.com/doublesharp/foundry) with [Solar](https://github.com/paradigmxyz/solar#binary-usage) for compatible development work. [Cargo install](https://doc.rust-lang.org/cargo/commands/cargo-install.html) supports pinned Git revisions, binary selection, required features, and reusable build output. Select a fork revision whose manifest provides `forgeds`; retain the project's wrappers, artifact paths, and approved release compiler.

## forgeds agent workflows, 2026-11-08

The `ds-solidity` reference covers changed-only warnings, reusable instrumented coverage, compact coverage gaps, and CI cache reuse. It draws on the fork's feature guide and the implementation and tests at `4ca15fcba25aa61a1b436d28b428e30b459f3d56`. [forgeds feature guide](https://github.com/doublesharp/foundry/blob/402b5f166132929d556f431dd3d8f9ccb698e99d/FORGEDS.md)

- [Compiler warning configuration](https://github.com/doublesharp/foundry/blob/4ca15fcba25aa61a1b436d28b428e30b459f3d56/crates/config/src/lib.rs) and [build tests](https://github.com/doublesharp/foundry/blob/4ca15fcba25aa61a1b436d28b428e30b459f3d56/crates/forge/tests/cli/build.rs) establish `compiler_warnings = "changed"`, profile inheritance, and visibility of errors and denied warnings.
- [Coverage command](https://github.com/doublesharp/foundry/blob/4ca15fcba25aa61a1b436d28b428e30b459f3d56/crates/forge/src/cmd/coverage.rs) and [coverage tests](https://github.com/doublesharp/foundry/blob/4ca15fcba25aa61a1b436d28b428e30b459f3d56/crates/forge/tests/cli/coverage.rs) establish compiler-output reuse with solc and Solar, fresh execution and coverage metadata on reruns, and `--report gaps` with `--report-file`. Instrumentation retains optimizer/viaIR settings but changes bytecode and gas.
- [Shared compiler caching](https://github.com/doublesharp/foundry/blob/4ca15fcba25aa61a1b436d28b428e30b459f3d56/docs/dev/solidity-compiler-cache.md) defines stable compiler inputs, local locking, and optional sccache storage for CI. Shared compiler results and project caches serve different purposes; preserve both.

Use the project's approved release compiler and required coverage modes.

## cargo-steward, 2026-11-07

On machines with cargo-steward, `RUSTC_WRAPPER=sccache` bypasses the steward's rustc wrapper. The `cargo` proxy and `cargo steward remove --worktree` already handle targets and cleanup under Cargo's locks. `ds-rust` uses the managed workflow when it detects cargo-steward and points to the skill installed by `cargo steward skill install`. It keeps the ordinary Cargo guidance for other machines.

## Worktree startup, 2026-11-06

The reported failure was: “The dev startup hit a dependency-link issue in the new worktree; I’m correcting the launch path before taking baseline captures.” It does not identify the package manager or exact error. General setup and working-directory checks belong to ds-work; Node dependency-link inspection and repair belong to ds-typescript. ds-web and ds-ux confirm the served checkout before captures. The decision scenarios cover each boundary, preserving the two-attempt environment repair limit.

## Optional security review, 2026-11-08

`ds-security` adapts the source-grounded finding discipline and supply-chain trust questions from [Cloudflare's security-audit-skill](https://github.com/cloudflare/security-audit-skill/tree/d24bc269171a9171fac58493e0ffba511d571a4a), especially its [entrypoint](https://github.com/cloudflare/security-audit-skill/blob/d24bc269171a9171fac58493e0ffba511d571a4a/skills/security-audit/SKILL.md) and [supply-chain companion](https://github.com/cloudflare/security-audit-skill/blob/d24bc269171a9171fac58493e0ffba511d571a4a/skills/security-audit/SUPPLY-CHAIN-AND-RELEASE.md). Exact consulted file hashes are in the source lock. The installed local copy was inspected to diagnose the reported failure; no instruction text was copied from it.

The MIT license is retained in [licenses/security-audit-LICENSE](../licenses/security-audit-LICENSE) and inside the standalone skill. The new instructions are written for dsstack: opt-in installation, ordinary project checks for dependency patches, containment chosen for hazardous execution, findings supported by source or execution, and bounded reviews without mandatory agents, ledgers, or report files. No upstream code or validators are imported. The triggering failure was a routine dependency patch that skipped all builds/tests because macOS could not enforce every audit-only memory control.

## Cross-provider councils, 2026-11-24

The council workflow draws on [tstack's council procedure](https://github.com/t3dotgg/tstack/blob/11e37a74d0a6868c121cd0910ab2b3bd9873b92a/skills/council/SKILL.md) for preparing the review target, running independent reviews in parallel, and checking findings as they arrive against a stable checkout. The caller contributes its own assessment and normally asks the other two providers.

## Updating

The UX rubric, six-round budget, and rotating-provider workflow are author choices maintained in the skill's own references.

When a pinned source changes, compare revisions file by file and decide which adaptations still serve the task. Use the decision scenarios to check changes to model-specific instructions. [Validation guide](validation.md)

## Shared compute broker

The shared compute broker and its reference come from this project's `feature/compute-broker` work. The `20261122-project-retention` bundle contributed named-resource leases. Configure hosts in the private resource profile. [Compute broker reference](../skills/ds-resources/references/compute.md)

## Authentication design policy

`ds-auth` records the requested passkey-first design across application stacks. It is independently written from the [WebAuthn specification](https://www.w3.org/TR/webauthn-3/), NIST SP 800-63B-4 [authenticators](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/), [assurance](https://pages.nist.gov/800-63-4/sp800-63b/aal/), and [recovery](https://pages.nist.gov/800-63-4/sp800-63b/events/), OWASP [MFA](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html) and [session](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) guidance, [OAuth security BCP](https://www.rfc-editor.org/rfc/rfc9700.html), and [MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization). No upstream instruction text or implementation is imported.

The profile boundaries, two-key activation rule, recovery promotion defaults, and suggested session limits are design choices. The policy keeps authentication strength separate from enrollment provenance: enrolling a key after restricted recovery cannot manufacture privileged trust. Existing application libraries, local-only products, provider identities, and encryption-key recovery retain their distinct boundaries. The skill and routing example carry the shared policy; project-specific adoption work stays private.
