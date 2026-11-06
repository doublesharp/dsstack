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

    def skill(self, name):
        p = self.root / "skills" / name
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

    def bundle_source(self):
        (self.root / "scripts").mkdir()
        shutil.copy2(ROOT / "scripts/dsstack.py", self.root / "scripts/dsstack.py")
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
        self.assertEqual(result["skills"], 2)

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
        profile = ds._profile(self.dest)
        self.assertEqual(profile["reserve_gib"], 12)
        self.assertFalse(profile["require_mount"])
        self.assertTrue(ds.doctor(self.dest)["ok"])
        ds.install(self.dest, self.base / "agent-skills")
        self.assertEqual((self.base / "agent-skills/ds-one").resolve(), installed.parent)

    def test_bundled_cli_uses_its_private_profile_after_source_is_removed(self):
        self.bundle_source()
        ds.bundle(self.root, self.dest, self.local, apply=True)
        shutil.rmtree(self.root)
        command = [sys.executable, str(self.dest / "scripts/dsstack.py")]
        checked = subprocess.run(command + ["doctor"], capture_output=True, text=True, check=True)
        self.assertTrue(json.loads(checked.stdout)["ok"])
        checked = subprocess.run(command + ["preflight", "--project", "app", "--task", "fix"],
                                 capture_output=True, text=True, check=True)
        result = json.loads(checked.stdout)
        self.assertEqual(result["scratch"], str(self.base))
        self.assertEqual(result["required_gib"], 12)
        self.assertFalse(result["creates_directories"])
        overridden = subprocess.run(command + ["preflight", "--project", "app", "--task", "fix",
                                               "--scratch", str(self.dest)], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(overridden.stdout)["scratch"], str(self.dest))

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

    def test_bundle_keeps_private_output_outside_source_and_rejects_missing_policy(self):
        self.bundle_source()
        for dest, local in ((self.root / ".local/bundle", None),
                            (self.dest, self.base / "missing-policy")):
            with self.subTest(dest=dest), self.assertRaises(ds.StackError):
                ds.bundle(self.root, dest, local, apply=True)
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
        result = ds.preflight(self.base, "app", "task", reserve_gib=0, require_mount=False)
        self.assertEqual(result["scratch"], str(self.base))

    def test_cli_requires_storage_instead_of_assuming_a_machine_path(self):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            status = ds.main(["--stack-root", str(self.root), "preflight", "--project", "app", "--task", "fix"])
        self.assertEqual(status, 2)
        self.assertIn("--scratch", json.loads(errors.getvalue())["error"])

    def test_profile_validation_rejects_silent_typo_and_invalid_values(self):
        profile = self.base / "profile.json"
        for invalid in ({"reserve_gib": -1}, {"require_mount": "false"}, {"reserve_gib": True},
                        {"reseve_gib": 10}, [], {"scratch": "relative/path"}):
            profile.write_text(json.dumps(invalid))
            with self.subTest(invalid=invalid), self.assertRaises(ds.StackError):
                ds._profile(self.root, profile)

    def test_preflight_reserves_peak_plus_headroom_and_creates_nothing(self):
        scratch = self.base / "Scratch"
        scratch.mkdir()
        usage = shutil._ntuple_diskusage(1000 * 2**30, 800 * 2**30, 200 * 2**30)
        with patch.object(Path, "is_mount", return_value=True), patch.object(ds.shutil, "disk_usage", return_value=usage):
            with self.assertRaises(ds.StackError):
                ds.preflight(scratch, "app", "task-one", expected_gib=60, reserve_gib=150)
            result = ds.preflight(scratch, "app", "task-one", expected_gib=40, reserve_gib=150)
        self.assertEqual(result["paths"]["build"], str(scratch / "app/build/task-one"))
        self.assertEqual(list(scratch.iterdir()), [])

    def test_explicit_missing_profile_is_rejected_instead_of_using_defaults(self):
        output, errors = io.StringIO(), io.StringIO()
        missing = self.base / "misspelled-profile.json"
        with patch.object(ds, "preflight", return_value={"ok": True}) as admit:
            with redirect_stdout(output), redirect_stderr(errors):
                status = ds.main(["--stack-root", str(self.root), "preflight", "--project", "app", "--task", "fix", "--profile", str(missing)])
        self.assertEqual(status, 2)
        self.assertIn(str(missing), json.loads(errors.getvalue())["error"])
        admit.assert_not_called()

    def test_preflight_rejects_an_unmounted_scratch(self):
        scratch = self.base / "Scratch"
        scratch.mkdir()
        with self.assertRaises(ds.StackError):
            ds.preflight(scratch, "app", "task-one")

    def test_preflight_rejects_unsafe_names(self):
        with patch.object(Path, "is_mount", return_value=True):
            for project, task in [("../app", "ok"), ("app", "../../source"), (".", "ok")]:
                with self.subTest(project=project, task=task), self.assertRaises(ds.StackError):
                    ds.preflight(self.base, project, task)

    def test_preflight_rejects_output_symlink_escape(self):
        scratch = self.base / "Scratch"
        (scratch / "app").mkdir(parents=True)
        (scratch / "app/build").symlink_to(self.base, target_is_directory=True)
        usage = shutil._ntuple_diskusage(1000 * 2**30, 100 * 2**30, 900 * 2**30)
        with patch.object(Path, "is_mount", return_value=True), patch.object(ds.shutil, "disk_usage", return_value=usage):
            with self.assertRaises(ds.StackError):
                ds.preflight(scratch, "app", "task-one")

    def test_preflight_rejects_non_finite_or_negative_budgets(self):
        with patch.object(Path, "is_mount", return_value=True):
            for expected in [-1, float("nan"), float("inf")]:
                with self.subTest(expected=expected), self.assertRaises(ds.StackError):
                    ds.preflight(self.base, "app", "task-one", expected_gib=expected)


if __name__ == "__main__":
    unittest.main()
