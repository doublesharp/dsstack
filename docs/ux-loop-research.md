# AI competition loops applied to UX

Primary sources read 2026-11-03. These are design inputs for ds-ux, not evidence that model-scored UI improvements reproduce the papers' results. The collection's seven-category rubric and six-round, alternating-provider council define the actual workflow.

- **FunSearch**, Romera-Paredes et al., Nature, 2023; [paper](https://www.nature.com/articles/s41586-023-06924-6), [authors' explanation](https://deepmind.google/blog/funsearch-making-new-discoveries-in-mathematical-sciences-using-large-language-models/). It generates programs, evaluates them separately, and reuses high-scoring programs. It also maintains diversity to avoid stagnation. Adaptation: retain the best interface, make each candidate compete against it, and try a revised or different coherent fix after rejection. We use one serial candidate per round, without population search or parallel writers.
- **AlphaEvolve**, Google DeepMind, 2025; [authors' explanation](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/). An ensemble proposes programs; automated evaluators verify and score them; stored results inform subsequent proposals. Adaptation: separate implementation from evaluation, preserve a recoverable best, and keep functional checks alongside the design score. AlphaEvolve's objective executable evaluation does not establish the reliability of subjective UX scores.
- **Self-Refine**, Madaan et al., NeurIPS 2023; [paper, sections 2 and 4](https://arxiv.org/html/2303.17651v2). Iterative refinement uses specific feedback, earlier outputs and feedback history, and a stopping condition. Adaptation: the next provider gets rejected hypotheses, the concrete failed task, proposed fix, and previous decision rather than merely “make it better.” The workflow uses an independent council, so we do not adopt the paper's same-model self-feedback as authoritative scoring.
- **Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena**, Zheng et al., NeurIPS 2023; [paper, sections 3.3–3.4](https://arxiv.org/html/2306.05685v4). It documents position, verbosity, and self-enhancement biases, and tests order-swapped judging. Adaptation: fresh evaluators, shared evidence, no implementer identity in scoring briefs, opposite presentation orders, and independent verdicts. Our two-reviewer procedure is a practical adaptation; opposite orders across different judges do not prove each judge's order consistency.
- **MLE-bench**, Chan et al., 2024; [paper, sections 2.1–2.3](https://arxiv.org/html/2410.07095v1). Kaggle-derived tasks use specified metrics and separate grading. Section 2.2 explicitly chooses private leaderboards because submissions sometimes overfit the public leaderboard. Adaptation: fix the rubric, data, devices, and journey checks before iterating. A higher screenshot score cannot excuse a broken task or removed content. We do not introduce a hidden UX dataset or extra benchmark infrastructure.

The conservative council rule—minimum score per category/device cell, with neither individual matrix allowed to regress—is our implementation choice, not a result established by these papers. It preserves 0.5-point category increments and 70/30 formula while preventing one generous judge from masking the other's regression finding. It can also reject gains both judges see in different cells when the combined minimum stays unchanged. This favors a stable retained best; the rejected evidence becomes feedback within the finite round budget.

The loop is: baseline → one candidate → independent Codex and Claude scores → retain an accepted improvement or keep the previous best → alternate the implementer. Stop rules live in ds-work. Keep numerical design judgments tied to observed task gains; they are not measured task-completion rates. No upstream source code or skill prose was copied.

## Theo's UI hill climb, reviewed 2026-11-05

Theo Browne, [Agents Sucked At UI (Until Today)](https://www.youtube.com/watch?v=xq0eB8vxeqk), 2026-11-03. Read the timestamped captions through this [transcript mirror](https://ainotes.us/summary/agents-sucked-at-ui-until-today); YouTube's fetched page did not expose captions. The following maps the reusable lessons to ds-ux, not the mirror's generated summary.

| Video segment | Reflection in ds-ux |
|---|---|
| 02:13–04:12: sponsor's coded design variants | Existing implementation rounds produce working UI; no sponsor dependency. |
| 05:22–09:27: criticism, council, noisy ratings | Concrete priorities, independent reviewers, fixed rubric, observed gains. |
| 09:48–10:58: unreliable “jester” | Existing inspect-only roles and evidence requirements; no entertainment reviewer. |
| 11:22–12:37: subtle polish, annotated comparisons, score history | Rubric details, matched callouts when needed, round table. |
| 12:55–16:01: competitor comparisons change judgments | Fixed external references, same-pass rankings, paired scores. |
| 16:42–19:38: staged reviewers and higher goals | Preserve the configured full council and finite budget; quota cannot produce solo acceptance. |
| 19:38–20:49: unchanged references drift; target bias | Identify calibration drift; hide desired scores from judges. |
| 21:16–22:56: cost and narrow screens | Existing budget, viewport stress checks; no copied spending assumptions. |
| 23:20–26:22: color, clear actions, light-mode syntax | User taste, purposeful color, supported-theme coverage. |
| 26:48–31:21: executable evaluations and simplification | Objective checks accompany design scores; MCP compression remains outside this UI skill. |

The two-provider roster, alternating writers, conservative aggregate, and six-round default remain collection-specific choices. The video does not establish their effectiveness. No transcript or upstream skill prose was copied.
