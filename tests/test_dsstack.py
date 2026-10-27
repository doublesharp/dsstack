from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
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
        scratch = Path("/Volumes/Scratch")
        cls.tmpdir = Path(os.environ.get("TMPDIR", "")).expanduser().resolve()
        if not scratch.is_mount() or not cls.tmpdir.is_relative_to(scratch.resolve()):
            raise RuntimeError("Set TMPDIR to a writable task directory under mounted /Volumes/Scratch")

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
