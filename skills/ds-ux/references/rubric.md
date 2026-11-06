# UX comparison rubric

Use the same seven categories for mobile, tablet, and desktop. Score each from 0 to 10 in 0.5-point steps against inspected tasks and states. Overall is calculated, not an eighth judgment.

Cover the primary journey's applicable initial and scrolled views, navigation, forms, menus/dialogs, loading, empty, error, and success states in supported themes. Check relevant touch, pointer, keyboard, and focus behavior; skip states that do not apply. Each device score reflects these states beyond the landing screenshot; a light-mode defect cannot be hidden by a dark-mode score.

| Category | Look for |
|---|---|
| Typography | Readability, loaded/fallback fonts, scale, line length, weight, wrapping, meaningful truncation, zoom |
| Hierarchy | Primary action, order, grouping, emphasis, scanning |
| Spacing & density | Alignment, rhythm, useful space, target separation |
| Color & contrast | Readable text/controls and syntax, semantic color, visible states, non-color cues |
| Iconography | Recognizable meaning, labels, size, alignment, coherent style |
| Consistency & polish | Coherent labels, radii, borders, indicators, responsive states, absence of visual defects |
| Clarity | Labels, discoverability, feedback, recovery, next step |

0 means unusable; 1–2 severe obstruction; 3–4 frequent friction; 5–6 usable with weaknesses; 7–8 strong; 9 excellent; 10 exceptional with explicit supporting observations. Measure relevant foreground/background contrast before claiming contrast compliance.

For each device, take the mean of its seven categories. The aggregate is `0.7 × mean(three device totals) + 0.3 × lowest device total`. Calculate from unrounded category values; display derived totals to one decimal. Expose the lowest category and device, including ties. Keep the full category matrix available for regression checks.

The 360px and zoom checks can reveal acceptance-blocking problems but do not add scoring devices. An unavailable stress check alone does not make an observed category unscorable unless the ask requires it for acceptance; report that gap. Do not average “Not evaluated” cells as zero or omit them to manufacture an aggregate. Report partial category observations and leave the overall pending when a scoring device lacks evidence.

Preserve the baseline scope, data, and rubric within each comparison. Carry unchanged scores forward unless new observations justify a correction. Correct an erroneous baseline explicitly and recompute its comparisons; do not count that correction as candidate progress. Each verdict uses its evaluator's matched previous-best/candidate pair. Combine the two matrices using [paired scoring](scoring.md).

A task failure, broken keyboard/focus order, or removed essential content blocks acceptance regardless of score. Relate score changes to concrete observations, such as a visible primary action or preserved return state.

User taste is a design constraint: translate “too grayscale” into purposeful emphasis and clearer actions, rather than adding arbitrary color or flattening everything to chase a score. Existing contrast, focus, and non-color cues still apply. Use objective measurements for verifiable claims; model ratings do not measure task success or replace functional checks.

Show `Category | Mobile | Tablet | Desktop | Main evidence`, including all seven categories and calculated Overall. For candidates, show previous → candidate values and deltas. Follow with the aggregate, lowest category/device, three prioritized fixes, and ACCEPT/REVISE decision or pending evidence. Unchanged scores are not a scored design gain; report any separately observed interaction benefit.

Custom iconography is a candidate improvement, not an automatic score increase. Compare the set at actual control sizes and across supported themes; preserve labels, accessible names, contrast, and familiar meanings. A coherent set matters more than bespoke decoration.
