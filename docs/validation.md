# Validation

Set TMPDIR to an existing task-owned directory under mounted /Volumes/Scratch and set PYTHONDONTWRITEBYTECODE=1. This revision's tests require that output policy.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/dsstack.py doctor
```

The standard-library tests check installation ownership and conflicts, metadata, references, and resource preflight. Doctor can also check installed links with --dest. Passing these checks does not establish that an agent follows the skills; use the decision scenarios to inspect its choices.
