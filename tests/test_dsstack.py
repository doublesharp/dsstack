from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dsstack_cli", ROOT / "scripts/dsstack.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
resources = ds._resources


class StackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configured = os.environ.get("TMPDIR")
        if not configured or not Path(configured).is_dir():
            raise RuntimeError("Set TMPDIR to an existing task-owned output directory")
        cls.tmpdir = Path(configured).resolve()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="dsstack-test-", dir=self.tmpdir)
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "stack"
        self.dest = self.base / "installed"
        self.skill("ds-one")
        self.skill("ds-two")

    def skill(self, name, optional=False):
        p = self.root / ("optional-skills" if optional else "skills") / name
        p.mkdir(parents=True)
        (p / "SKILL.md").write_text("---\nname: " + json.dumps(name) + "\ndescription: \"Use when exercising a focused fixture.\"\n---\n# Fixture\n")
        return p

    def test_install_plan_is_read_only_and_lists_new_links(self):
        plan = ds.plan_install(self.root, self.dest)
        self.assertEqual([x["action"] for x in plan], ["add", "add"])
        self.assertFalse(self.dest.exists())

    def test_apply_installs_complete_skills_and_is_idempotent(self):
        ds.install(self.root, self.dest)
        for name in ["ds-one", "ds-two"]:
            self.assertTrue((self.dest / name).is_symlink())
            self.assertEqual((self.dest / name).resolve(), (self.root / "skills" / name).resolve())
        self.assertEqual([x["action"] for x in ds.plan_install(self.root, self.dest)], ["keep", "keep"])
        ds.install(self.root, self.dest)

    def test_optional_install_requires_opt_in_and_is_preserved_on_default_update(self):
        source = self.skill("ds-extra", optional=True)
        ds.install(self.root, self.dest)
        self.assertFalse((self.dest / "ds-extra").exists())
        ds.install(self.root, self.dest, include_optional=["ds-extra"])
        self.assertEqual((self.dest / "ds-extra").resolve(), source)
        ds.install(self.root, self.dest)
        self.assertEqual((self.dest / "ds-extra").resolve(), source)
        self.assertTrue(ds.doctor(self.root, self.dest)["ok"])

    def test_unknown_optional_and_selected_conflict_prevent_every_install(self):
        self.skill("ds-extra", optional=True)
        with self.assertRaises(ds.StackError):
            ds.install(self.root, self.dest, include_optional=["ds-typo"])
        self.assertFalse(self.dest.exists())
        self.dest.mkdir()
        (self.dest / "ds-extra").write_text("foreign skill")
        with self.assertRaises(ds.StackError):
            ds.install(self.root, self.dest, include_optional=["ds-extra"])
        self.assertFalse((self.dest / "ds-one").exists())
        self.assertEqual((self.dest / "ds-extra").read_text(), "foreign skill")

    def test_uninstall_removes_owned_optionals_and_preserves_unselected_foreign_optionals(self):
        self.skill("ds-extra", optional=True)
        self.skill("ds-foreign", optional=True)
        ds.install(self.root, self.dest, include_optional=["ds-extra"])
        (self.dest / "ds-foreign").write_text("keep")
        ds.uninstall(self.root, self.dest)
        self.assertFalse((self.dest / "ds-extra").is_symlink())
        self.assertFalse((self.dest / "ds-one").is_symlink())
        self.assertEqual((self.dest / "ds-foreign").read_text(), "keep")

    def test_doctor_checks_optional_references_and_scenarios_without_installing(self):
        source = self.skill("ds-extra", optional=True)
        self.scenarios("## Optional review\n\nSkills: ds-extra\n\nRequest: review a boundary.\n")
        self.assertTrue(ds.doctor(self.root)["ok"])
        path = source / "SKILL.md"
        path.write_text(path.read_text() + "Read [missing](references/missing.md).\n")
        self.assertFalse(ds.doctor(self.root)["ok"])
        self.assertFalse(self.dest.exists())

    def test_list_marks_optional_skills_without_selecting_them(self):
        self.skill("ds-extra", optional=True)
        output = io.StringIO()
        with redirect_stdout(output):
            status = ds.main(["--stack-root", str(self.root), "list"])
        self.assertEqual(status, 0)
        result = {item["name"]: item for item in json.loads(output.getvalue())}
        self.assertTrue(result["ds-extra"]["optional"])
        self.assertFalse(result["ds-one"]["optional"])
        self.assertFalse(self.dest.exists())

    def test_optional_name_collision_and_escaping_symlink_are_rejected(self):
        source = self.skill("ds-one", optional=True)
        with self.assertRaises(ds.StackError):
            ds.install(self.root, self.dest)
        shutil.rmtree(source)
        (self.root / "optional-skills/ds-extra").symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(ds.StackError):
            ds.install(self.root, self.dest, include_optional=["ds-extra"])
        self.assertFalse(self.dest.exists())

    def test_one_conflict_prevents_every_install(self):
        self.dest.mkdir()
        conflict = self.dest / "ds-two"
        conflict.write_text("my custom skill")
        with self.assertRaises(ds.StackError):
            ds.install(self.root, self.dest)
        self.assertEqual(conflict.read_text(), "my custom skill")
        self.assertFalse((self.dest / "ds-one").exists())

    def test_foreign_symlink_is_not_replaced(self):
        self.dest.mkdir()
        other = self.base / "other"
        other.mkdir()
        (self.dest / "ds-one").symlink_to(other, target_is_directory=True)
        with self.assertRaises(ds.StackError):
            ds.install(self.root, self.dest)
        self.assertEqual((self.dest / "ds-one").resolve(), other)

    def owned_links(self):
        self.dest.mkdir()
        for name in ["ds-one", "ds-two"]:
            (self.dest / name).symlink_to(self.root / "skills" / name, target_is_directory=True)

    def test_uninstall_removes_only_owned_links_and_preserves_sources(self):
        self.owned_links()
        (self.dest / "unrelated").write_text("keep")
        ds.uninstall(self.root, self.dest)
        self.assertFalse((self.dest / "ds-one").is_symlink())
        self.assertTrue((self.root / "skills/ds-one/SKILL.md").exists())
        self.assertEqual((self.dest / "unrelated").read_text(), "keep")

    def test_uninstall_refuses_retargeted_link_without_partial_changes(self):
        self.owned_links()
        (self.dest / "ds-two").unlink()
        (self.dest / "ds-two").symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(ds.StackError):
            ds.uninstall(self.root, self.dest)
        self.assertTrue((self.dest / "ds-one").is_symlink())
        self.assertEqual((self.dest / "ds-two").resolve(), self.base)

    def retired_link(self):
        retired = self.dest / "ds-retired"
        retired.symlink_to(self.root / "skills" / "ds-retired", target_is_directory=True)
        return retired

    def test_install_prunes_only_stale_links_into_this_stack(self):
        self.owned_links()
        retired = self.retired_link()
        foreign = self.dest / "ds-foreign"
        foreign.symlink_to(self.base / "elsewhere" / "ds-foreign", target_is_directory=True)
        plan = {x["name"]: x["action"] for x in ds.plan_install(self.root, self.dest)}
        self.assertEqual(plan, {"ds-one": "keep", "ds-two": "keep", "ds-retired": "prune"})
        self.assertTrue(retired.is_symlink())
        ds.install(self.root, self.dest)
        self.assertFalse(retired.is_symlink())
        self.assertTrue(foreign.is_symlink())
        self.assertEqual([x["action"] for x in ds.plan_install(self.root, self.dest)], ["keep", "keep"])

    def test_stale_link_fails_doctor_and_uninstall_removes_it(self):
        self.owned_links()
        self.retired_link()
        result = ds.doctor(self.root, self.dest)
        self.assertFalse(result["ok"])
        self.assertIn("ds-retired", " ".join(result["errors"]))
        ds.uninstall(self.root, self.dest)
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_doctor_rejects_missing_reference(self):
        p = self.root / "skills/ds-one/SKILL.md"
        p.write_text(p.read_text() + "Read [details](references/missing.md).\n")
        result = ds.doctor(self.root)
        self.assertFalse(result["ok"])
        self.assertIn("missing.md", " ".join(result["errors"]))

    def test_doctor_rejects_wrong_skill_name(self):
        p = self.root / "skills/ds-one/SKILL.md"
        p.write_text(p.read_text().replace('"ds-one"', '"ds-elsewhere"'))
        self.assertFalse(ds.doctor(self.root)["ok"])

    def scenarios(self, text):
        path = self.root / "evals/scenarios.md"
        path.parent.mkdir()
        path.write_text(text)

    def test_doctor_accepts_scenarios_using_catalog_skills(self):
        self.scenarios("# Scenarios\n\n## Shared task\n\nSkills: ds-one, ds-two\n\nRequest: finish the task.\n")
        self.assertTrue(ds.doctor(self.root)["ok"])

    def test_doctor_rejects_unknown_scenario_skill(self):
        self.scenarios("## Wrong skill\n\nSkills: ds-missing\n\nRequest: finish the task.\n")
        result = ds.doctor(self.root)
        self.assertFalse(result["ok"])
        self.assertIn("ds-missing", " ".join(result["errors"]))

    def test_doctor_requires_scenario_skill_declarations_on_each_request(self):
        self.scenarios("## Declared\n\nSkills: ds-one\n\nRequest: first task.\n\n## Missing\n\nRequest: second task.\n")
        result = ds.doctor(self.root)
        self.assertFalse(result["ok"])
        self.assertIn("Missing", " ".join(result["errors"]))

    def test_doctor_rejects_empty_or_ambiguous_scenario_declarations(self):
        for declarations in ("Skills:\n", "Skills: ds-one\nSkills: ds-two\n"):
            with self.subTest(declarations=declarations):
                path = self.root / "evals/scenarios.md"
                path.parent.mkdir(exist_ok=True)
                path.write_text("## Broken\n\n" + declarations + "\nRequest: finish the task.\n")
                self.assertFalse(ds.doctor(self.root)["ok"])

    def bundle_source(self):
        (self.root / "scripts").mkdir()
        shutil.copy2(ROOT / "scripts/dsstack.py", self.root / "scripts/dsstack.py")
        shutil.copytree(ROOT / "skills/ds-resources", self.root / "skills/ds-resources")
        for name in ("VERSION", "LICENSE", "NOTICE"):
            (self.root / name).write_text("fixture\n")
        refs = self.root / "skills/ds-one/references"
        refs.mkdir()
        (refs / "detail.md").write_text("original reference\n")
        self.local = self.base / "private"
        (self.local / "skills").mkdir(parents=True)
        (self.local / "policy.md").write_text("Keep worktrees on backed-up storage.\n")
        (self.local / "skills/ds-one.md").write_text("Use /private-builds for this machine.\n")
        (self.local / "resource-profile.json").write_text(json.dumps({
            "scratch": str(self.base), "reserve_gib": 12,
            "warning_gib": 24, "require_mount": False,
        }))

    def test_bundle_preview_creates_nothing_and_does_not_expose_policy(self):
        self.bundle_source()
        result = ds.bundle(self.root, self.dest, self.local)
        self.assertFalse(self.dest.exists())
        self.assertNotIn("/private-builds", json.dumps(result))
        self.assertEqual(result["skills"], 3)

    def optional_bundle_source(self):
        self.bundle_source()
        source = self.skill("ds-extra", optional=True)
        (source / "references").mkdir()
        (source / "references/detail.md").write_text("optional detail\n")
        path = source / "SKILL.md"
        path.write_text(path.read_text() + "Read [detail](references/detail.md).\n")
        (source / "agents").mkdir()
        (source / "agents/openai.yaml").write_text('interface:\n  default_prompt: "Use $ds-extra."\n')
        return source

    def test_optional_bundle_is_explicit_frozen_and_installs_without_source(self):
        source = self.optional_bundle_source()
        default_bundle = self.base / "default-bundle"
        ds.bundle(self.root, default_bundle, apply=True)
        self.assertFalse((default_bundle / "skills/ds-extra").exists())
        self.assertFalse((default_bundle / "optional-skills").exists())
        preview = ds.bundle(self.root, self.dest, include_optional=["ds-extra"])
        self.assertEqual(preview["skills"], 4)
        self.assertFalse(self.dest.exists())
        ds.bundle(self.root, self.dest, apply=True, include_optional=["ds-extra"])
        frozen = self.dest / "skills/ds-extra"
        self.assertEqual((frozen / "references/detail.md").read_text(), "optional detail\n")
        self.assertEqual((frozen / "agents/openai.yaml").read_text(), (source / "agents/openai.yaml").read_text())
        shutil.rmtree(self.root)
        agents = self.base / "agents"
        ds.install(self.dest, agents)
        self.assertEqual((agents / "ds-extra").resolve(), frozen)
        self.assertTrue(ds.doctor(self.dest, agents)["ok"])

    def test_optional_bundle_policy_applies_only_when_selected(self):
        self.optional_bundle_source()
        (self.local / "skills/ds-extra.md").write_text("Additional optional policy.\n")
        with self.assertRaises(ds.StackError):
            ds.bundle(self.root, self.dest, self.local, apply=True)
        self.assertFalse(self.dest.exists())
        ds.bundle(self.root, self.dest, self.local, apply=True, include_optional=["ds-extra"])
        text = (self.dest / "skills/ds-extra/SKILL.md").read_text()
        self.assertIn("Additional optional policy.", text)
        self.assertIn("backed-up storage", text)

    def test_optional_bundle_rejects_unknown_names_and_source_links_before_writes(self):
        source = self.optional_bundle_source()
        with self.assertRaises(ds.StackError):
            ds.bundle(self.root, self.dest, apply=True, include_optional=["ds-typo"])
        self.assertFalse(self.dest.exists())
        (source / "leak").symlink_to(self.local / "policy.md")
        with self.assertRaises(ds.StackError):
            ds.bundle(self.root, self.dest, apply=True, include_optional=["ds-extra"])
        self.assertFalse(self.dest.exists())

    def test_optional_cli_flags_preview_and_apply_bundles_and_installs(self):
        self.optional_bundle_source()
        self.skill("ds-more", optional=True)
        flags = ["--include-optional", "ds-extra", "--include-optional", "ds-more"]
        for command in ("install", "bundle"):
            destination = self.base / command
            args = ["--stack-root", str(self.root), command, "--dest", str(destination)] + flags
            for apply in (False, True):
                output = io.StringIO()
                with redirect_stdout(output):
                    status = ds.main(args + (["--apply"] if apply else []))
                self.assertEqual(status, 0, output.getvalue())
                self.assertEqual(destination.exists(), apply)
            skill_root = destination / "skills" if command == "bundle" else destination
            self.assertTrue((skill_root / "ds-extra/SKILL.md").is_file())
            self.assertTrue((skill_root / "ds-more/SKILL.md").is_file())

    def test_bundle_freezes_sources_and_inlines_private_instructions(self):
        self.bundle_source()
        original = (self.root / "skills/ds-one/SKILL.md").read_text()
        ds.bundle(self.root, self.dest, self.local, apply=True)
        installed = self.dest / "skills/ds-one/SKILL.md"
        self.assertIn("backed-up storage", installed.read_text())
        self.assertIn("/private-builds", installed.read_text())
        self.assertIn("backed-up storage", (self.dest / "skills/ds-two/SKILL.md").read_text())
        self.assertNotIn("/private-builds", (self.dest / "skills/ds-two/SKILL.md").read_text())
        self.assertEqual((self.root / "skills/ds-one/SKILL.md").read_text(), original)
        (self.root / "skills/ds-one/SKILL.md").write_text("upstream changed")
        (self.local / "policy.md").write_text("private policy changed")
        self.assertIn("backed-up storage", installed.read_text())
        self.assertNotIn("upstream changed", installed.read_text())
        profile = resources.load_profile(self.dest / "skills/ds-resources")
        self.assertEqual(profile["reserve_gib"], 12)
        self.assertFalse(profile["require_mount"])
        self.assertFalse((self.dest / "profiles").exists())
        self.assertTrue(ds.doctor(self.dest)["ok"])
        ds.install(self.dest, self.base / "agent-skills")
        self.assertEqual((self.base / "agent-skills/ds-one").resolve(), installed.parent)

    def test_bundled_resource_cli_uses_its_private_profile_after_source_is_removed(self):
        self.bundle_source()
        ds.bundle(self.root, self.dest, self.local, apply=True)
        shutil.rmtree(self.root)
        command = [sys.executable, str(self.dest / "scripts/dsstack.py")]
        checked = subprocess.run(command + ["doctor"], capture_output=True, text=True, check=True)
        self.assertTrue(json.loads(checked.stdout)["ok"])
        command = [sys.executable, str(self.dest / "skills/ds-resources/scripts/preflight.py")]
        checked = subprocess.run(command + ["--project", "app", "--task", "fix"],
                                 capture_output=True, text=True, check=True)
        result = json.loads(checked.stdout)
        self.assertEqual(result["scratch"], str(self.base))
        self.assertEqual(result["required_gib"], 12)
        self.assertFalse(result["creates_directories"])
        overridden = subprocess.run(command + ["--project", "app", "--task", "fix",
                                               "--scratch", str(self.dest)], capture_output=True, text=True)
        self.assertEqual(overridden.returncode, 2)
        self.assertIn("profile", json.loads(overridden.stderr)["error"].lower())

    def test_bundle_requires_resource_skill_for_private_resource_policy(self):
        self.bundle_source()
        shutil.rmtree(self.root / "skills/ds-resources")
        with self.assertRaises(ds.StackError):
            ds.bundle(self.root, self.dest, self.local)
        self.assertFalse(self.dest.exists())

    def test_bundle_omits_unrelated_root_resource_files(self):
        self.bundle_source()
        (self.root / "profiles").mkdir()
        (self.root / "profiles/unrelated.json").write_text('{"scratch": "/unrelated"}')
        ds.bundle(self.root, self.dest, self.local, apply=True)
        self.assertFalse((self.dest / "profiles").exists())

    def test_read_only_cli_does_not_create_bytecode_without_environment_override(self):
        self.bundle_source()
        for cache in self.root.rglob("__pycache__"):
            shutil.rmtree(cache)
        env = os.environ.copy()
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        env.pop("PYTHONPYCACHEPREFIX", None)
        before = {str(path.relative_to(self.root)) for path in self.root.rglob("*")}
        checked = subprocess.run([sys.executable, str(self.root / "scripts/dsstack.py"), "doctor"],
                                 capture_output=True, text=True, env=env)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual({str(path.relative_to(self.root)) for path in self.root.rglob("*")}, before)

    def test_copied_resource_skill_runs_without_stack_and_uses_private_profile(self):
        self.bundle_source()
        ds.bundle(self.root, self.dest, self.local, apply=True)
        isolated = self.base / "resource-only"
        shutil.copytree(self.dest / "skills/ds-resources", isolated)
        shutil.rmtree(self.root)
        shutil.rmtree(self.dest)
        command = [sys.executable, str(isolated / "scripts/preflight.py"),
                   "--project", "app", "--task", "fix"]
        checked = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        result = json.loads(checked.stdout)
        self.assertEqual(result["scratch"], str(self.base))
        self.assertEqual(result["required_gib"], 12)
        self.assertFalse((self.base / "app").exists())

    def test_bundle_cli_preview_and_apply(self):
        self.bundle_source()
        args = ["--stack-root", str(self.root), "bundle", "--dest", str(self.dest), "--local", str(self.local)]
        for apply in (False, True):
            output = io.StringIO()
            with redirect_stdout(output):
                status = ds.main(args + (["--apply"] if apply else []))
            self.assertEqual(status, 0)
            self.assertEqual(self.dest.exists(), apply)
            self.assertEqual(json.loads(output.getvalue())["applied"], apply)

    def test_bundle_rejects_unignored_output_and_missing_policy(self):
        self.bundle_source()
        for dest, local in ((self.root / ".local/bundle", None),
                            (self.dest, self.base / "missing-policy")):
            with self.subTest(dest=dest), self.assertRaises(ds.StackError):
                ds.bundle(self.root, dest, local, apply=True)
            self.assertFalse(dest.exists())

    def test_bundle_supports_ignored_local_directory_without_copying_private_inputs(self):
        self.bundle_source()
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        (self.root / ".gitignore").write_text("/.local/\n")
        local = self.root / ".local/policy"
        local.parent.mkdir()
        shutil.move(self.local, local)
        dest = self.root / ".local/bundles/current"
        ds.bundle(self.root, dest, local)
        self.assertFalse(dest.exists())
        ds.bundle(self.root, dest, local, apply=True)
        self.assertIn("/private-builds", (dest / "skills/ds-one/SKILL.md").read_text())
        self.assertFalse((dest / ".local").exists())
        self.assertTrue(ds.doctor(dest)["ok"])
        status = subprocess.check_output(["git", "status", "--short", "--untracked-files=all"], cwd=self.root, text=True)
        self.assertNotIn(".local/", status)

    def test_bundle_refuses_tracked_files_under_local(self):
        self.bundle_source()
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        (self.root / ".gitignore").write_text("/.local/\n")
        (self.root / ".local").mkdir()
        (self.root / ".local/tracked.md").write_text("already tracked")
        subprocess.run(["git", "add", "--force", ".local/tracked.md"], cwd=self.root, check=True)
        dest = self.root / ".local/bundles/current"
        with self.assertRaises(ds.StackError):
            ds.bundle(self.root, dest, self.local, apply=True)
        self.assertFalse(dest.exists())

    def test_bundle_refuses_local_destination_that_resolves_into_public_source(self):
        self.bundle_source()
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        (self.root / ".gitignore").write_text("/.local/\n")
        (self.root / ".local").mkdir()
        (self.root / ".local/bundles").symlink_to(self.root / "skills", target_is_directory=True)
        dest = self.root / ".local/bundles/current"
        with self.assertRaises(ds.StackError):
            ds.bundle(self.root, dest, self.local, apply=True)
        self.assertFalse(dest.exists())

    def test_other_bundle_install_cannot_retarget_existing_agent_links(self):
        self.bundle_source()
        ds.bundle(self.root, self.dest, apply=True)
        agents = self.base / "agent-skills"
        ds.install(self.root, agents)
        with self.assertRaises(ds.StackError):
            ds.install(self.dest, agents)
        self.assertEqual((agents / "ds-one").resolve(), self.root / "skills/ds-one")
        ds.uninstall(self.root, agents)
        ds.install(self.dest, agents)
        self.assertTrue(ds.doctor(self.dest, agents)["ok"])

    def test_bundle_refuses_overwrite_even_during_preview(self):
        self.bundle_source()
        ds.bundle(self.root, self.dest, apply=True)
        with self.assertRaises(ds.StackError):
            ds.bundle(self.root, self.dest, self.local, apply=True)
        self.assertNotIn("/private-builds", (self.dest / "skills/ds-one/SKILL.md").read_text())

    def test_bundle_rejects_unknown_overlay_and_escaping_source_links(self):
        self.bundle_source()
        (self.local / "skills/ds-typo.md").write_text("important rule")
        with self.assertRaises(ds.StackError):
            ds.bundle(self.root, self.dest, self.local, apply=True)
        self.assertFalse(self.dest.exists())
        (self.local / "skills/ds-typo.md").unlink()
        (self.root / "skills/ds-one/leak").symlink_to(self.local / "policy.md")
        with self.assertRaises(ds.StackError):
            ds.bundle(self.root, self.dest, apply=True)
        self.assertFalse(self.dest.exists())

    def test_bundle_cleans_failed_assembly_without_changing_installed_skills(self):
        self.bundle_source()
        ds.install(self.root, self.base / "agent-skills")
        (self.local / "skills/ds-one.md").write_text("See [missing](missing.md).")
        with self.assertRaises(ds.StackError):
            ds.bundle(self.root, self.dest, self.local, apply=True)
        self.assertFalse(self.dest.exists())
        self.assertEqual((self.base / "agent-skills/ds-one").resolve(), self.root / "skills/ds-one")

    def test_preflight_accepts_explicit_non_mount_directory(self):
        result = resources.preflight(self.base, "app", "task", reserve_gib=0, require_mount=False)
        self.assertEqual(result["scratch"], str(self.base))

    def test_stack_cli_does_not_dispatch_resource_commands(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
            ds.main(["preflight", "--project", "app", "--task", "fix"])
        self.assertEqual(stopped.exception.code, 2)

    def test_cli_requires_storage_instead_of_assuming_a_machine_path(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(resources, "ROOT", self.root), redirect_stdout(output), redirect_stderr(errors):
            status = resources.main(["--project", "app", "--task", "fix"])
        self.assertEqual(status, 2)
        self.assertIn("--scratch", json.loads(errors.getvalue())["error"])

    def test_resource_cli_reports_profile_guidance_without_enforcing_scheduling(self):
        profile = self.base / "policy.json"
        profile.write_text(json.dumps({"scratch": str(self.base), "require_mount": False,
                                       "recommendations": {"heavy_build_slots": 1}, "notes": ["Use configured output"]}))
        output = io.StringIO()
        with redirect_stdout(output):
            status = resources.main(["--profile", str(profile), "--project", "app", "--task", "fix"])
        self.assertEqual(status, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["recommendations"], {"heavy_build_slots": 1})
        self.assertEqual(result["notes"], ["Use configured output"])
        self.assertFalse(result["scheduling_enforced"])

    def test_resource_cli_preserves_profile_reserve_and_allows_larger_reserves(self):
        profile = self.base / "policy.json"
        profile.write_text(json.dumps({"scratch": str(self.base), "require_mount": False,
                                       "reserve_gib": 12}))
        usage = shutil._ntuple_diskusage(100 * 2**30, 80 * 2**30, 20 * 2**30)
        for reserve, expected_status in ((0, 2), (12, 0), (16, 0)):
            with self.subTest(reserve=reserve):
                output, errors = io.StringIO(), io.StringIO()
                with patch.object(resources.shutil, "disk_usage", return_value=usage), redirect_stdout(output), redirect_stderr(errors):
                    status = resources.main(["--profile", str(profile), "--project", "app", "--task", "fix",
                                             "--reserve-gib", str(reserve)])
                self.assertEqual(status, expected_status)
                if status:
                    self.assertIn("reserve", json.loads(errors.getvalue())["error"].lower())
                else:
                    self.assertEqual(json.loads(output.getvalue())["required_gib"], reserve)

    def test_profile_validation_rejects_silent_typo_and_invalid_values(self):
        profile = self.base / "profile.json"
        for invalid in ({"reserve_gib": -1}, {"require_mount": "false"}, {"reserve_gib": True},
                        {"reseve_gib": 10}, [], {"scratch": "relative/path"}):
            profile.write_text(json.dumps(invalid))
            with self.subTest(invalid=invalid), self.assertRaises(ds.StackError):
                resources.load_profile(self.root, profile)

    def test_preflight_reserves_peak_plus_headroom_and_creates_nothing(self):
        scratch = self.base / "Scratch"
        scratch.mkdir()
        usage = shutil._ntuple_diskusage(1000 * 2**30, 800 * 2**30, 200 * 2**30)
        with patch.object(Path, "is_mount", return_value=True), patch.object(resources.shutil, "disk_usage", return_value=usage):
            with self.assertRaises(ds.StackError):
                resources.preflight(scratch, "app", "task-one", expected_gib=60, reserve_gib=150)
            result = resources.preflight(scratch, "app", "task-one", expected_gib=40, reserve_gib=150)
        self.assertEqual(result["paths"]["build"], str(scratch / "app/build/task-one"))
        self.assertEqual(list(scratch.iterdir()), [])

    def test_explicit_missing_profile_is_rejected_instead_of_using_defaults(self):
        output, errors = io.StringIO(), io.StringIO()
        missing = self.base / "misspelled-profile.json"
        with patch.object(resources, "preflight", return_value={"ok": True}) as admit:
            with redirect_stdout(output), redirect_stderr(errors):
                status = resources.main(["--project", "app", "--task", "fix", "--profile", str(missing)])
        self.assertEqual(status, 2)
        self.assertIn(str(missing), json.loads(errors.getvalue())["error"])
        admit.assert_not_called()

    def test_preflight_rejects_an_unmounted_scratch(self):
        scratch = self.base / "Scratch"
        scratch.mkdir()
        with self.assertRaises(ds.StackError):
            resources.preflight(scratch, "app", "task-one")

    def test_preflight_rejects_unsafe_names(self):
        with patch.object(Path, "is_mount", return_value=True):
            for project, task in [("../app", "ok"), ("app", "../../source"), (".", "ok")]:
                with self.subTest(project=project, task=task), self.assertRaises(ds.StackError):
                    resources.preflight(self.base, project, task)

    def test_preflight_rejects_output_symlink_escape(self):
        scratch = self.base / "Scratch"
        (scratch / "app").mkdir(parents=True)
        (scratch / "app/build").symlink_to(self.base, target_is_directory=True)
        usage = shutil._ntuple_diskusage(1000 * 2**30, 100 * 2**30, 900 * 2**30)
        with patch.object(Path, "is_mount", return_value=True), patch.object(resources.shutil, "disk_usage", return_value=usage):
            with self.assertRaises(ds.StackError):
                resources.preflight(scratch, "app", "task-one")

    def test_preflight_rejects_non_finite_or_negative_budgets(self):
        with patch.object(Path, "is_mount", return_value=True):
            for expected in [-1, float("nan"), float("inf")]:
                with self.subTest(expected=expected), self.assertRaises(ds.StackError):
                    resources.preflight(self.base, "app", "task-one", expected_gib=expected)


if __name__ == "__main__":
    unittest.main()
