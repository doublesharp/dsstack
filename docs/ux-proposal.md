# Measured UX workflow

`ds-ux` serves explicitly requested UX hill climbs with alternating Codex/Claude implementation and independent council scoring. Ordinary interface edits use ds-web. The workflow adds no runtime, browser tooling, or global installation.

## Origin and design choices

Private web-application sessions supplied the initial seven-category rubric, half-point scores, 70/30 aggregate, and six-round budget. Those sessions exposed failures that shaped the workflow:

- Different fixtures or viewports made comparisons misleading: hold the comparison scope and data fixed.
- Higher aggregate scores hid mobile regressions: retain category-level checks.
- Screenshot scaling and stale resize reports confused reviewers: verify actual viewport dimensions and match captures.
- Changing judges changed calibration: give fresh judges their provider's prior matrix and preserve distinct score series.
- Startup failures prevented valid evaluation: repair the environment before scoring, within the existing repair budget.
- Implementers' scores biased acceptance: the coordinator uses independent council results.

Private transcripts and thread links are omitted. They support these failure examples, not a claim that the workflow improves outcomes. [Competition-loop research](ux-loop-research.md) documents the external design inputs and their limits; no upstream skill text was copied.

## Decision scenarios

- Desktop improves but one mobile category falls: revise, even if the aggregate rises.
- Only production captures exist for a local edit: obtain matched local observations before evaluating the candidate.
- The sixth candidate is rejected: keep the previous best and report the budget reached.
- Two consecutive scored candidates do not improve: stop without resetting the count when providers switch.
- One evaluator lowers a category while the other raises it: a favorable summary cannot override the individual regression.
- A reviewer starts from different calibration: compare retained and candidate versions together before accepting its scores.

These scenarios test decisions. They do not establish the reliability of subjective numerical scores. The skill and its references are the maintained workflow; this document records why it took that shape.
