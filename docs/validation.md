# Validation

## Installer and bundle checks

After changing the installer, bundle assembly, profiles, or skill references, run the test suite and `doctor` from the repository root. Set `TMPDIR` to an existing task-owned directory under the repository's output policy.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/dsstack.py doctor
```

The tests cover link ownership and conflicts, read-only previews, bundle isolation, private additions, metadata, references, and resource preflight. `doctor` checks skill metadata and local references. In the source checkout it also checks `Skills:` declarations in the decision scenarios. Pass `--dest` to check the links in a host's skill directory. [Decision scenarios](../evals/scenarios.md)

## Skill behavior checks

1. Set a trial budget and choose the affected scenarios and a small representative fixture.
2. Give fresh agents the same task in separate sessions, one with the pre-edit skill text and one with the candidate. Keep the expected result and the other run out of each session.
3. Compare what the agents actually completed, what checks they ran, how they handled scope, and when they stopped.
4. Keep additions that correct the observed failure and cuts that preserve required behavior. Investigate disagreements, rerun only inconclusive cases, and reuse results from unaffected cases.

Use these trials for changes to skill behavior. Keep raw outputs in the configured disposable directory and report the outcome briefly. [Design rationale](focus.md)
