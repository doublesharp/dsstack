# Validation

Run the standard-library test suite and doctor after changing the installer, bundle assembly, profiles, or skill references. Set `TMPDIR` to an existing task-owned directory chosen under the repository's output policy and set `PYTHONDONTWRITEBYTECODE=1`.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/dsstack.py doctor
```

The tests cover filesystem ownership and conflicts, read-only plans, bundle isolation and private additions, metadata and references, and resource preflight. Doctor checks skill metadata and local references; with `--dest`, it also checks installed links.

A passing suite does not prove an agent follows the instructions. Use [decision scenarios](../evals/scenarios.md) for that, and judge the decisions rather than matching wording. Evaluate changed workflows with a representative task before activating them broadly. [Design rationale](focus.md) describes the behavior to observe.
