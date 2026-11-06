#!/usr/bin/env python3
"""Build and install portable skill bundles; check resource capacity without mutation."""
import argparse
import json
import math
from pathlib import Path
import re
import shutil
import sys

VERSION = "0.3.0"
ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
TASK_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")


class StackError(Exception):
    """An actionable validation or filesystem conflict."""


def _scalar(value):
    value = value.strip()
    if value.startswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise StackError(f"Invalid quoted metadata: {exc.msg}") from exc
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def _read_skill(path):
    text = (path / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", text, re.S)
    if not match:
        raise StackError(f"{path.name}: missing YAML frontmatter")
    metadata = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator or key not in ("name", "description", "license"):
            raise StackError(f"{path.name}: unsupported metadata line {line!r}")
        if key in metadata:
            raise StackError(f"{path.name}: duplicate {key}")
        metadata[key] = _scalar(value)
    name, description = metadata.get("name"), metadata.get("description")
    if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64 or name != path.name:
        raise StackError(f"{path.name}: metadata name must match its skill folder")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        raise StackError(f"{path.name}: provide a concise description")
    if any(marker in text for marker in ("[TODO:", "[INSERT", "[REPLACE")):
        raise StackError(f"{name}: unfinished scaffold")
    return {"name": name, "description": description, "path": str(path.resolve()), "text": text}


def catalog(root):
    root = Path(root).resolve()
    base = root / "skills"
    if not base.is_dir():
        raise StackError(f"No skills directory: {base}")
    skills = []
    for path in sorted(base.iterdir()):
        if path.name.startswith("."):
            continue
        if not path.is_dir() or not path.resolve().is_relative_to(base):
            raise StackError(f"Unexpected skill path: {path}")
        skills.append(_read_skill(path))
    if not skills:
        raise StackError("No skills found")
    return skills


def _owned_link(path, source):
    return path.is_symlink() and path.resolve() == source.resolve()


def _stale_links(root, destination, names):
    """Links into this stack's skills directory for skills it no longer ships."""
    base = Path(root).resolve() / "skills"
    if not destination.is_dir():
        return []
    stale = []
    for path in sorted(destination.iterdir()):
        if path.name in names or not path.is_symlink():
            continue
        target = path.resolve()
        if target.parent == base and target.name not in names:
            stale.append({"name": path.name, "action": "prune", "path": str(path), "source": str(target)})
    return stale


def plan_install(root, destination):
    destination = Path(destination).expanduser().absolute()
    plan = []
    skills = catalog(root)
    for skill in skills:
        source = Path(skill["path"])
        path = destination / skill["name"]
        if _owned_link(path, source):
            action = "keep"
        elif path.exists() or path.is_symlink():
            action = "conflict"
        else:
            action = "add"
        plan.append({"name": skill["name"], "action": action, "path": str(path), "source": str(source)})
    return plan + _stale_links(root, destination, {skill["name"] for skill in skills})


def _reject_conflicts(plan):
    conflicts = [item["path"] for item in plan if item["action"] == "conflict"]
    if conflicts:
        raise StackError("Existing skills were preserved; resolve these conflicts first: " + ", ".join(conflicts))


def install(root, destination):
    plan = plan_install(root, destination)
    _reject_conflicts(plan)
    created = []
    try:
        for item in plan:
            if item["action"] == "add":
                path = Path(item["path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(item["source"], target_is_directory=True)
                created.append(item)
    except OSError:
        for item in reversed(created):
            path = Path(item["path"])
            if _owned_link(path, Path(item["source"])):
                path.unlink()
        raise
    _remove_owned(plan, "prune")
    return plan


def _remove_owned(plan, action):
    for item in plan:
        if item["action"] == action:
            path = Path(item["path"])
            if not _owned_link(path, Path(item["source"])):
                raise StackError(f"Installation changed; preserved {path}")
            path.unlink()


def plan_uninstall(root, destination):
    plan = plan_install(root, destination)
    for item in plan:
        item["action"] = {"keep": "remove", "add": "absent", "conflict": "conflict", "prune": "remove"}[item["action"]]
    return plan


def uninstall(root, destination):
    plan = plan_uninstall(root, destination)
    _reject_conflicts(plan)
    _remove_owned(plan, "remove")
    return plan


def doctor(root, destination=None):
    errors, warnings = [], []
    try:
        skills = catalog(root)
    except (StackError, OSError) as exc:
        return {"ok": False, "skills": 0, "errors": [str(exc)], "warnings": []}
    for skill in skills:
        path = Path(skill["path"])
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", skill["text"]):
            target = target.strip("<>").split("#", 1)[0]
            if not target or re.match(r"[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            if not (path / target).exists():
                errors.append(f"{skill['name']}: missing reference {target}")
        if len(skill["text"].split()) > 600:
            warnings.append(f"{skill['name']}: long entrypoint; consider moving conditional detail to a reference")
        ui = path / "agents/openai.yaml"
        if ui.exists():
            ui_text = ui.read_text(encoding="utf-8")
            if "$" + skill["name"] not in ui_text:
                errors.append(f"{skill['name']}: UI prompt must name the skill")
    if destination is not None:
        for item in plan_install(root, destination):
            if item["action"] != "keep":
                errors.append(f"{item['name']}: {item['action']} at {item['path']}")
        if (Path(destination).expanduser() / "using-superpowers").exists():
            warnings.append("Superpowers bootstrap is present; review active configuration for competing workflow instructions")
    return {"ok": not errors, "skills": len(skills), "errors": errors, "warnings": warnings}


def _copy_inputs(root):
    """Only runtime instructions, tooling, and attribution belong in a bundle."""
    inputs = ["skills", "scripts/dsstack.py", "VERSION", "LICENSE", "NOTICE"]
    inputs += [name for name in ("licenses", "upstreams.lock.json", "profiles")
               if (root / name).exists()]
    for name in inputs:
        path = root / name
        if not path.exists():
            raise StackError(f"Missing bundle input: {path}")
        paths = [path, *path.rglob("*")] if path.is_dir() else [path]
        for child in paths:
            if child.is_symlink() or not (child.is_file() or child.is_dir()):
                raise StackError(f"Bundle inputs must be regular files or directories: {child}")
    return inputs


def _local_policy(local, names):
    if local is None:
        return {}, None
    local = Path(local).expanduser().resolve()
    if not local.is_dir():
        raise StackError(f"No local policy directory: {local}")
    allowed = {"policy.md", "skills", "resource-profile.json"}
    for path in local.iterdir():
        if path.name not in allowed or path.is_symlink():
            raise StackError(f"Unexpected local policy entry: {path}")
    additions = {}
    common = (local / "policy.md").read_text(encoding="utf-8").strip() if (local / "policy.md").exists() else ""
    fragments = local / "skills"
    if fragments.exists():
        if not fragments.is_dir():
            raise StackError(f"Expected a directory: {fragments}")
        for path in fragments.iterdir():
            if path.suffix != ".md" or path.stem not in names or not path.is_file() or path.is_symlink():
                raise StackError(f"Unknown skill or invalid local addition: {path}")
            additions[path.stem] = path.read_text(encoding="utf-8").strip()
    for name in names:
        text = "\n\n".join(part for part in (common, additions.get(name, "")) if part)
        if text:
            additions[name] = text
    profile = _profile(local, local / "resource-profile.json") if (local / "resource-profile.json").exists() else None
    return additions, profile


def bundle(root, destination, local=None, apply=False):
    """Preview or create a new frozen stack, without touching installed skills."""
    root = Path(root).resolve()
    destination = Path(destination).expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise StackError(f"Bundle destination already exists: {destination}")
    if destination.resolve().is_relative_to(root):
        raise StackError("Keep bundles outside the source checkout so private policy cannot be published with it")
    skills = catalog(root)
    inputs = _copy_inputs(root)
    additions, profile = _local_policy(local, {skill["name"] for skill in skills})
    check = doctor(root)
    if not check["ok"]:
        raise StackError("; ".join(check["errors"]))
    result = {"ok": True, "destination": str(destination), "skills": len(skills),
              "customized_skills": sorted(additions), "resource_profile": profile is not None,
              "applied": apply}
    if not apply:
        return result
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir(mode=0o700)  # Exclusive creation; never replace an existing bundle.
    try:
        for name in inputs:
            source, target = root / name, destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        for name, text in additions.items():
            path = destination / "skills" / name / "SKILL.md"
            with path.open("a", encoding="utf-8") as stream:
                stream.write("\n## Local policy\n\n" + text + "\n")
        if profile is not None:
            path = destination / "profiles/default.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
        check = doctor(destination)
        if not check["ok"]:
            raise StackError("; ".join(check["errors"]))
    except Exception:
        shutil.rmtree(destination)
        raise
    result["warnings"] = check["warnings"]
    return result


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


def _profile(root, override=None):
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
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--stack-root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List available skills")
    check = sub.add_parser("doctor", help="Check metadata, references, and optional installed links")
    check.add_argument("--dest", type=Path)
    for name in ("install", "uninstall"):
        command = sub.add_parser(name, help="Preview owned skill links; add --apply to change them")
        command.add_argument("--dest", type=Path, required=True)
        command.add_argument("--apply", action="store_true")
    frozen = sub.add_parser("bundle", help="Preview a frozen stack with optional private additions")
    frozen.add_argument("--dest", type=Path, required=True)
    frozen.add_argument("--local", type=Path)
    frozen.add_argument("--apply", action="store_true")
    resource = sub.add_parser("preflight", help="Read-only mount, capacity, and task namespace check")
    resource.add_argument("--scratch", type=Path)
    resource.add_argument("--project", required=True)
    resource.add_argument("--task", required=True)
    resource.add_argument("--expected-gib", type=float, default=0)
    resource.add_argument("--reserve-gib", type=float)
    resource.add_argument("--profile", type=Path)
    args = parser.parse_args(argv)
    try:
        root = args.stack_root.resolve()
        if args.command == "list":
            result = [{k: v for k, v in item.items() if k != "text"} for item in catalog(root)]
        elif args.command == "doctor":
            result = doctor(root, args.dest)
        elif args.command == "bundle":
            result = bundle(root, args.dest, args.local, args.apply)
        elif args.command == "install":
            result = install(root, args.dest) if args.apply else plan_install(root, args.dest)
        elif args.command == "uninstall":
            result = uninstall(root, args.dest) if args.apply else plan_uninstall(root, args.dest)
        else:
            profile = _profile(root, args.profile)
            scratch = args.scratch if args.scratch is not None else profile.get("scratch")
            if scratch is None:
                raise StackError("Set --scratch PATH or a resource profile with scratch; no machine path is assumed")
            result = preflight(scratch, args.project, args.task, args.expected_gib,
                               profile["reserve_gib"] if args.reserve_gib is None else args.reserve_gib,
                               profile["warning_gib"], profile["require_mount"])
        print(json.dumps(result, indent=2))
        if isinstance(result, dict) and not result.get("ok", True):
            return 1
        if isinstance(result, list) and any(item.get("action") == "conflict" for item in result):
            return 1
        return 0
    except (StackError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
