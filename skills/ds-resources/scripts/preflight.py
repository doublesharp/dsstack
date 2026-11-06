#!/usr/bin/env python3
"""Check task output paths and capacity without creating or scheduling anything."""
import argparse
import json
import math
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
TASK_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")


class StackError(ValueError):
    """An invalid output policy or unavailable resource."""


def preflight(scratch, project, task, expected_gib=0, reserve_gib=0, warning_gib=0, require_mount=True):
    for label, value in (("project", project), ("task", task)):
        if not TASK_NAME.fullmatch(value):
            raise StackError(f"Unsafe {label} name: use 1-64 letters, digits, dots, underscores, or hyphens, beginning with a letter or digit")
    for label, value in (("expected", expected_gib), ("reserve", reserve_gib), ("warning", warning_gib)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise StackError(f"{label} GiB must be finite and non-negative")
    scratch = Path(scratch).expanduser().absolute()
    if scratch.is_symlink() or not scratch.is_dir() or (require_mount and not scratch.is_mount()):
        kind = "mount" if require_mount else "directory"
        raise StackError(f"Output root must be an existing, non-symlink {kind}: {scratch}")
    paths = {kind: str(scratch / project / directory / task) for kind, directory in (("build", "build"), ("tmp", "tmp"), ("reports", "reports"))}
    for output in paths.values():
        current = scratch
        for part in Path(output).relative_to(scratch).parts:
            current = current / part
            if current.is_symlink() or (current.exists() and not current.is_dir()):
                raise StackError(f"Output namespace is not an owned directory path: {current}")
    free_gib = shutil.disk_usage(scratch).free / 2**30
    required = expected_gib + reserve_gib
    if free_gib < required:
        raise StackError(f"Insufficient output/container space: {free_gib:.1f} GiB free; need {expected_gib:.1f} GiB peak plus {reserve_gib:.1f} GiB reserve")
    warnings = []
    if free_gib < warning_gib:
        warnings.append(f"Free capacity is below the {warning_gib:g} GiB target")
    return {"ok": True, "scratch": str(scratch), "project": project, "task": task, "free_gib": round(free_gib, 2), "required_gib": required, "paths": paths, "warnings": warnings, "creates_directories": False, "scheduling_enforced": False}


def load_profile(root, override=None):
    path = Path(override).expanduser() if override is not None else Path(root) / "profiles/default.json"
    profile = json.loads(path.read_text(encoding="utf-8")) if override is not None or path.exists() else {}
    allowed = {"name", "scratch", "reserve_gib", "warning_gib", "require_mount", "recommendations", "notes"}
    if not isinstance(profile, dict) or profile.keys() - allowed:
        raise StackError(f"Invalid resource profile fields: {path}")
    for key in ("reserve_gib", "warning_gib"):
        value = profile.get(key, 0)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise StackError(f"{key} must be finite and non-negative: {path}")
    if not isinstance(profile.get("require_mount", True), bool):
        raise StackError(f"require_mount must be true or false: {path}")
    if "scratch" in profile:
        value = profile["scratch"]
        if not isinstance(value, str) or not Path(value).expanduser().is_absolute():
            raise StackError(f"scratch must be an absolute path: {path}")
    return {"reserve_gib": 0, "warning_gib": 0, "require_mount": True, **profile}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", type=Path)
    parser.add_argument("--project", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--expected-gib", type=float, default=0)
    parser.add_argument("--reserve-gib", type=float)
    parser.add_argument("--profile", type=Path)
    args = parser.parse_args(argv)
    try:
        profile = load_profile(ROOT, args.profile)
        if args.reserve_gib is not None and args.reserve_gib < profile["reserve_gib"]:
            raise StackError("The reserve cannot be lower than the profile's configured reserve")
        if args.scratch is not None and "scratch" in profile:
            requested = args.scratch.expanduser().resolve()
            configured = Path(profile["scratch"]).expanduser().resolve()
            if requested != configured:
                raise StackError("The profile already selects an output root; select or update the profile instead of overriding it")
        scratch = args.scratch if args.scratch is not None else profile.get("scratch")
        if scratch is None:
            raise StackError("Set --scratch PATH or a resource profile with scratch; no machine path is assumed")
        result = preflight(scratch, args.project, args.task, args.expected_gib,
                           profile["reserve_gib"] if args.reserve_gib is None else args.reserve_gib,
                           profile["warning_gib"], profile["require_mount"])
        result.update({key: profile[key] for key in ("recommendations", "notes") if key in profile})
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
