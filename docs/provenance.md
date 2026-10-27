# Sources and deliberate adaptations

Exact source revisions and file hashes are in [upstreams.lock.json](../upstreams.lock.json). Upstream MIT license notices are retained in [licenses](../licenses). No upstream executable or session hook is installed by this collection.

| Source | Borrowed idea | Deliberate adaptation |
|---|---|---|
| t3dotgg/tstack sol-loop | Bounded review, focused later rounds, one reviewer, explicit disagreement | Rare security/finance/concurrency failures retain their impact. No mandatory model brand or council. |
| t3dotgg/tstack council | Independent named reviewers and synthesis | Explicit council only; two default seats, shared bounded rounds, no agreement loop or silent fallback. |
| t3dotgg/tstack full-stop | Own preparation through a clear readiness gate | No emphasis-triggered activation. User authority and current harness policy remain binding. |
| obra/superpowers | Behavioral RED/GREEN and root-cause hypotheses | No test-per-helper requirement, blanket workspace rerun, repeated revert cycle, or configuration approval ritual. |
| Existing project contracts | Scratch ownership and domain proof boundaries | Preserve the project's commands, versions, tracker, and release gates. |

Official references used for domain guidance:

- [Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html) and [configuration](https://doc.rust-lang.org/cargo/reference/config.html).
- [sccache Rust limitations](https://github.com/mozilla/sccache/blob/main/docs/Rust.md).
- [Fastify testing](https://fastify.dev/docs/latest/Guides/Testing/).
- [Tauri testing boundaries](https://tauri.app/develop/tests/).
- [Foundry guides](https://getfoundry.sh/guides).
- [OpenAI skill guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).

Other evaluated stacks were not bundled: chhoumann/t3-pstack has valuable T3 integration but broad routing; GitHub Spec Kit and GSD add planning/state workflows that are unnecessary for this initial collection.

For an update, inspect the pinned source's new revision, compare the relevant files, keep or revise the adaptation intentionally, update license notices when needed, and run the focused tests plus relevant decision scenarios. Source activity and stars are not evidence of improved task completion. Do not automatically merge upstream or reintroduce obsolete model-specific instructions.

The reciprocal consultation route also uses the local `claude-code` skill’s scoped private-code handoff, read-only consultation, and completion requirements. Its checked hash is recorded under `local_sources` in the lock. The Codex command syntax was checked against installed `codex exec --help`; local CLI syntax does not establish remote model availability. Standalone references are conditional; T3 routing remains governed by the current harness. Pstack’s panel synthesis informed the comparison; none of its hooks, automatic routing, or executables were copied.
