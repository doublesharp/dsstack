# Validation

Run the standard-library test suite and doctor after changing the installer, bundle assembly, profiles, or skill references. Set `TMPDIR` to an existing task-owned directory chosen under the repository's output policy and set `PYTHONDONTWRITEBYTECODE=1`.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/dsstack.py doctor
```

The tests cover filesystem ownership and conflicts, read-only plans, bundle isolation and private additions, metadata and references, and resource preflight. Doctor checks skill metadata, local references, and the `Skills:` declarations in [decision scenarios](../evals/scenarios.md); with `--dest`, it also checks installed links. Bundles work without the authoring scenarios.

A passing suite does not prove an agent follows instructions. For a behavioral skill change, select the affected scenarios and a small representative fixture. Give separate fresh agents the same task with the previous skill text and the candidate; do not show either the expected answer or the other run. Use the pre-edit revision as the baseline, and compare task completion, actual actions, relevant checks, scope, and stopping behavior. Explaining the right plan alone does not show that the agent followed it.

Set a trial budget before running models. Retain an addition only when it corrects the observed failure; retain a cut when required behavior is preserved. Investigate disagreements rather than starting an agreement loop, and rerun only a case whose result is inconclusive. Reuse unaffected results and do not turn these trials into a gate for ordinary application edits. Keep raw outputs in the configured disposable area and report the short conclusion.

[Design rationale](focus.md) describes the behavior to observe during normal work.
