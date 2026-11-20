"""Behavior tests for the compute broker. A fake ssh runs the "remote" side locally under a temporary HOME."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/ds-resources/scripts/compute.py"
spec = importlib.util.spec_from_file_location("dsstack_compute", SCRIPT)
C = importlib.util.module_from_spec(spec)
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
spec.loader.exec_module(C)
sys.dont_write_bytecode = _bytecode

FAKE_SSH = """#!/bin/sh
# fake ssh: skip -o options and the host, run the remainder locally (command string or rsync -e)
while [ "$1" = "-o" ]; do shift 2; done
shift
if [ $# -eq 1 ]; then exec sh -c "$1"; fi
exec "$@"
"""
FAIL_SSH = "#!/bin/sh\necho 'ssh: connect to host builder: Connection refused' >&2\nexit 255\n"
HOST = "builder"


def wait_for(path, seconds=10):
    end = time.time() + seconds
    while time.time() < end:
        if path.exists() and path.read_text().strip():
            return path.read_text().strip()
        time.sleep(0.1)
    raise AssertionError(f"timed out waiting for {path}")


class ComputeCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configured = os.environ.get("TMPDIR")
        if not configured or not Path(configured).is_dir():
            raise RuntimeError("Set TMPDIR to an existing task-owned output directory")
        cls.tmpdir = Path(configured).resolve()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="compute-test-", dir=self.tmpdir)
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.state, self.home = base / "state", base / "home"
        self.state.mkdir()
        self.home.mkdir()
        for name, text in (("fakessh", FAKE_SSH), ("badssh", FAIL_SSH)):
            (base / name).write_text(text)
            (base / name).chmod(0o755)
        self.fake, self.bad = str(base / "fakessh"), str(base / "badssh")
        self.profile = base / "profile.json"
        self.write_profile({"hosts": {HOST: {"python": sys.executable, "slots": {"shared": 4},
                                              "jobs": {"heavy": 14, "moderate": 4, "light": 2},
                                              "measure_marker": "~/bench/MEASURING"}},
                            "default_host": HOST})
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("COMPUTE_")}
        self.env.update(COMPUTE_STATE=str(self.state), COMPUTE_PROFILE=str(self.profile), HOME=str(self.home),
                        COMPUTE_SSH=self.fake, PYTHONDONTWRITEBYTECODE="1")
        self.set_loads(0, 0)
        proj = base / "work" / "myproj"
        (proj / "src").mkdir(parents=True)
        (proj / "target").mkdir()
        (proj / "target/big").write_text("x")
        (proj / ".git").mkdir()
        (proj / ".git/HEAD").write_text("ref")
        (proj / "src/a.txt").write_text("a")
        self.proj = proj
        self.procs = []
        self.addCleanup(self.reap)

    def reap(self):
        for p in self.procs:
            if p.poll() is None:
                p.kill()
            p.communicate()

    def write_profile(self, compute):
        """Pin the local machine's shape so tests do not depend on this host's cores or architecture."""
        local = {"slots": {"shared": 2}, "arch": "arm64", "jobs": {"heavy": 12, "moderate": 4, "light": 2},
                 **compute.get("local", {})}
        compute = {"poll_seconds": 0.1, "remote_poll_seconds": 0.3, **compute, "local": local}
        for host in compute.get("hosts", {}).values():
            host.setdefault("arch", "x86_64")
        self.profile.write_text(json.dumps({"compute": compute}))

    def set_loads(self, local_load, remote_load, local_cpus=12, remote_cpus=16):
        """Sampled load average is real and swings; every test pins it."""
        self.env["COMPUTE_FAKE_LOADS"] = json.dumps({"local": {"load1": local_load, "cpus": local_cpus},
                                                      HOST: {"load1": remote_load, "cpus": remote_cpus}})

    def compute(self, *args, timeout=60, ssh=None):
        env = dict(self.env, COMPUTE_SSH=ssh or self.fake)
        return subprocess.run([sys.executable, str(SCRIPT), *args], env=env, capture_output=True, text=True,
                              timeout=timeout)

    def popen(self, *args):
        p = subprocess.Popen([sys.executable, str(SCRIPT), *args], env=self.env, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
        self.procs.append(p)
        return p

    def pool(self, name, units, remote=False):  # noqa: D401
        root = (self.home / "compute" / "slots") if remote else (self.state / "slots")
        return C.Pool(str(root), name, units)


@unittest.skipUnless(shutil.which("rsync"), "rsync is required")
class ComputeTests(ComputeCase):
    # ---- pools and names -------------------------------------------------

    def test_pool_limits_and_weights(self):
        pool = C.Pool(self.tmp.name, "shared", 4)
        a, b = pool.try_acquire(2, {"id": "a"}), pool.try_acquire(2, {"id": "b"})
        self.assertTrue(a and b)
        self.assertIsNone(pool.try_acquire(1, {"id": "c"}))
        a.release()
        c = pool.try_acquire(1, {"id": "c"})
        self.assertEqual(pool.free_units(), 1)
        b.release()
        c.release()
        self.assertEqual(pool.free_units(), 4)

    def test_killed_holder_frees_its_slot(self):
        code = (f"import importlib.util as u,time;s=u.spec_from_file_location('c',{str(SCRIPT)!r});m=u.module_from_spec(s);"
                f"s.loader.exec_module(m);p=m.Pool({self.tmp.name!r},'heavy',1);l=p.try_acquire(1,{{'id':'x'}});"
                "print('held',flush=True);time.sleep(60)")
        child = subprocess.Popen([sys.executable, "-B", "-c", code], stdout=subprocess.PIPE, text=True)
        self.procs.append(child)
        self.assertEqual(child.stdout.readline().strip(), "held")
        pool = C.Pool(self.tmp.name, "heavy", 1)
        self.assertIsNone(pool.try_acquire(1, {}))
        child.kill()
        child.wait()
        lease = pool.try_acquire(1, {})
        self.assertIsNotNone(lease)
        lease.release()

    def test_unsafe_names_are_rejected(self):
        for bad in ("", ".", "..", "a/b", "../x", "x y", "-x"):
            with self.assertRaises(ValueError):
                C.safe_name(bad, "dir")
        self.assertEqual(C.safe_name("my-proj_1.2", "dir"), "my-proj_1.2")
        r = self.compute("run", "--class", "moderate", "--where", HOST, "--sync", str(self.proj), "--name", "../evil",
                         "--", "true")
        self.assertEqual(r.returncode, 2)

    # ---- local scheduling --------------------------------------------------

    def test_heavy_job_queues_behind_a_running_one(self):
        first = self.popen("run", "--class", "heavy", "--", "sleep", "2")
        time.sleep(0.8)
        t0 = time.time()
        second = self.compute("run", "--class", "heavy", "--", "echo", "second")
        self.assertEqual(second.returncode, 0)
        self.assertIn("second", second.stdout)
        self.assertIn("queued behind 1 jobs", second.stderr)
        self.assertIn("waited", second.stderr)
        self.assertGreaterEqual(time.time() - t0, 0.8)
        first.wait(timeout=10)

    def test_moderate_allows_two_and_light_is_unlimited(self):
        procs = [self.popen("run", "--class", "moderate", "--", "sleep", "2") for _ in range(2)]
        time.sleep(0.8)
        status = json.loads(self.compute("status", "--json").stdout)
        self.assertEqual(sum(1 for h in status["local"]["pools"]["shared"]["holders"] if h), 2)
        third = self.popen("run", "--class", "moderate", "--", "echo", "third")
        light = self.compute("run", "--class", "light", "--", "echo", "light")
        self.assertEqual((light.returncode, light.stdout.strip()), (0, "light"))
        time.sleep(0.5)
        self.assertIsNone(third.poll())
        out, err = third.communicate(timeout=15)
        self.assertIn("third", out)
        self.assertIn("queued behind 2 jobs", err)
        for p in procs:
            p.wait(timeout=10)

    def test_exit_code_and_job_count_reach_the_command(self):
        r = self.compute("run", "--class", "heavy", "--", "sh", "-c", "echo $COMPUTE_JOBS $COMPUTE_CLASS; exit 3")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(r.stdout.split(), ["12", "heavy"])

    def test_without_a_profile_it_schedules_locally_only(self):
        env = {k: v for k, v in self.env.items() if k != "COMPUTE_PROFILE"}
        env["COMPUTE_PROFILE"] = str(self.tmp.name + "/absent.json")
        r = subprocess.run([sys.executable, str(SCRIPT), "run", "--class", "heavy", "--sync", str(self.proj), "--",
                            "sh", "-c", "echo $COMPUTE_HOST $COMPUTE_JOBS"], env=env, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)  # an explicit profile path that is missing is an error
        env.pop("COMPUTE_PROFILE")
        env["HOME"] = str(self.home)
        r = subprocess.run([sys.executable, str(SCRIPT), "run", "--class", "heavy", "--sync", str(self.proj), "--",
                            "sh", "-c", "echo $COMPUTE_HOST $COMPUTE_JOBS"], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.split()[0], "local")
        self.assertEqual(int(r.stdout.split()[1]), max(2, (os.cpu_count() or 4) - 2))
        r = subprocess.run([sys.executable, str(SCRIPT), "run", "--class", "heavy", "--where", "anything", "--",
                            "true"], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("unknown host", r.stderr)

    def test_state_defaults_to_profile_scratch_and_refuses_a_missing_volume(self):
        scratch = Path(self.tmp.name) / "vol"
        scratch.mkdir()
        env = {k: v for k, v in self.env.items() if k != "COMPUTE_STATE"}
        self.profile.write_text(json.dumps({"scratch": str(scratch), "require_mount": False, "compute": {}}))
        r = subprocess.run([sys.executable, str(SCRIPT), "run", "--class", "heavy", "--", "true"], env=env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((scratch / ".compute/slots").is_dir())
        self.profile.write_text(json.dumps({"scratch": str(scratch / "missing"), "compute": {}}))
        r = subprocess.run([sys.executable, str(SCRIPT), "run", "--class", "heavy", "--", "true"], env=env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, C.EXIT_BROKER)
        self.assertIn("unavailable", r.stderr)

    def test_ctrl_c_while_running_releases_the_slot(self):
        p = self.popen("run", "--class", "heavy", "--", "sleep", "60")
        time.sleep(1)
        p.send_signal(signal.SIGINT)
        p.wait(timeout=20)
        self.assertEqual(p.returncode, 128 + signal.SIGINT)
        r = self.compute("run", "--class", "heavy", "--", "true", timeout=10)
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("queued", r.stderr)

    def test_ctrl_c_while_queued_leaves_no_queue_entry(self):
        holder = self.popen("run", "--class", "heavy", "--", "sleep", "3")
        time.sleep(0.8)
        q = self.popen("run", "--class", "heavy", "--", "true")
        time.sleep(0.8)
        q.send_signal(signal.SIGINT)
        q.wait(timeout=10)
        self.assertEqual(q.returncode, 130)
        self.assertEqual(os.listdir(self.state / "queue/shared"), [])
        holder.wait(timeout=10)

    def test_killed_broker_keeps_the_slot_until_the_job_exits(self):
        p = self.popen("run", "--class", "heavy", "--", "sleep", "3")
        time.sleep(0.8)
        p.kill()
        p.wait()
        pool = self.pool("shared", 2)
        self.assertIsNone(pool.try_acquire(2, {}))
        time.sleep(3.5)
        lease = pool.try_acquire(2, {})
        self.assertIsNotNone(lease)
        lease.release()

    # ---- measurement windows -----------------------------------------------

    def test_local_window_blocks_heavy_but_not_light_or_ignored(self):
        self.assertEqual(self.compute("measure", "begin", "--host", "local", "--reason", "t").returncode, 0)
        q = self.popen("run", "--class", "heavy", "--", "echo", "ran")
        time.sleep(1)
        self.assertIsNone(q.poll())
        self.assertEqual(self.compute("run", "--class", "light", "--", "true").returncode, 0)
        self.assertEqual(self.compute("run", "--class", "heavy", "--ignore-measure", "--", "true").returncode, 0)
        self.compute("measure", "end", "--host", "local")
        out, err = q.communicate(timeout=10)
        self.assertIn("ran", out)
        self.assertIn("measurement window", err)

    def test_second_begin_needs_force(self):
        self.assertEqual(self.compute("measure", "begin", "--host", "local").returncode, 0)
        self.assertNotEqual(self.compute("measure", "begin", "--host", "local").returncode, 0)
        self.assertEqual(self.compute("measure", "end", "--host", "local").returncode, 0)

    def test_remote_window_writes_marker_and_parks_remote_jobs(self):
        r = self.compute("measure", "begin", "--host", HOST, "--reason", "bench")
        self.assertEqual(r.returncode, 0, r.stderr)
        marker = self.home / "bench/MEASURING"
        self.assertEqual(json.loads(marker.read_text())["reason"], "bench")
        ok = self.compute("run", "--class", "heavy", "--sync", str(self.proj), "--", "sh", "-c", "echo $COMPUTE_HOST")
        self.assertEqual(ok.stdout.strip(), "local")  # auto never overflows into a measured host
        q = self.popen("run", "--class", "moderate", "--where", HOST, "--sync", str(self.proj), "--", "echo", "remote-ran")
        time.sleep(2)
        self.assertIsNone(q.poll())
        self.compute("measure", "end", "--host", HOST)
        self.assertFalse(marker.exists())
        out, err = q.communicate(timeout=30)
        self.assertIn("remote-ran", out)
        self.assertIn("measurement window", err)

    def test_wait_never_reports_drained_for_an_unreachable_host(self):
        r = self.compute("measure", "begin", "--host", HOST, "--wait", "2", ssh=self.bad)
        self.assertNotIn("host drained", r.stdout)
        self.assertNotEqual(r.returncode, 0)

    def test_pause_commands_come_from_the_profile_and_never_prompt_for_a_password(self):
        self.write_profile({"hosts": {HOST: {"python": sys.executable, "measure_marker": "~/bench/MEASURING",
                                              "pause_commands": [["sudo", "svc", "stop", "a,b"]],
                                              "resume_commands": [["sudo", "-n", "svc", "start", "a,b"]]}}})
        rule = self.compute("measure", "sudoers", "--host", HOST).stdout
        self.assertIn("NOPASSWD: svc stop a\\,b, \\\n  svc start a\\,b", rule)
        shown = self.compute("measure", "begin", "--host", HOST).stdout
        self.assertIn("sudo -n svc stop", shown)
        self.compute("measure", "end", "--host", HOST)

    # ---- remote execution ---------------------------------------------------

    def test_remote_run_syncs_sets_env_returns_artifacts_and_the_exit_code(self):
        env_dir = self.home / "compute/env"
        env_dir.mkdir(parents=True)
        (env_dir / "work.sh").write_text("export FROM_ENV_FILE=yes\n")
        script = ("import os,sys; print(os.getcwd()); print(os.environ['COMPUTE_JOBS'], os.environ['CARGO_TARGET_DIR']);"
                  "print(sorted(os.listdir('.'))); open('built.txt','w').write('artifact');"
                  "print(os.environ.get('FROM_ENV_FILE')); sys.exit(4)")
        r = self.compute("run", "--class", "heavy", "--where", HOST, "--sync", str(self.proj), "--artifacts", "built.txt",
                         "--", sys.executable, "-c", script)
        self.assertEqual(r.returncode, 4, r.stderr)
        lines = r.stdout.splitlines()
        self.assertTrue(lines[0].endswith("/compute/jobs/work/myproj"))
        jobs, target = lines[1].split()
        self.assertEqual(jobs, "14")
        self.assertTrue(target.endswith("/compute/cargo/work/myproj"))
        self.assertIn("src", lines[2])
        self.assertNotIn("target", lines[2])
        self.assertNotIn(".git", lines[2])
        self.assertEqual(lines[3], "yes")
        self.assertEqual((self.proj / "built.txt").read_text(), "artifact")

    def test_remote_arguments_survive_quoting(self):
        r = self.compute("run", "--class", "moderate", "--where", HOST, "--sync", str(self.proj), "--",
                         sys.executable, "-c", "import sys; print(sys.argv[1:])", "a b", "$HOME", "it's")
        self.assertEqual(r.stdout.strip(), "['a b', '$HOME', \"it's\"]")

    def test_compute_sync_file_can_keep_part_of_an_excluded_directory(self):
        (self.proj / ".compute-sync").write_text("+ .git/\n+ .git/HEAD\n- .git/**\n")
        r = self.compute("run", "--class", "moderate", "--where", HOST, "--sync", str(self.proj), "--",
                         sys.executable, "-c", "import os; print(sorted(os.listdir('.git')))")
        self.assertEqual(r.stdout.strip(), "['HEAD']")

    def test_profile_selects_remote_root_env_dir_and_path(self):
        self.write_profile({"hosts": {HOST: {"python": sys.executable, "root": "~/jobs-root", "env_dir": "~/envs",
                                              "path_prepend": ["/opt/custom/bin"]}}})
        (self.home / "envs").mkdir()
        (self.home / "envs/work.sh").write_text("export FROM_PROFILE_ENV=1\n")
        r = self.compute("run", "--class", "moderate", "--where", HOST, "--sync", str(self.proj), "--",
                         sys.executable, "-c",
                         "import os; print(os.getcwd()); print(os.environ['PATH'].split(':')[0], os.environ.get('FROM_PROFILE_ENV'))")
        lines = r.stdout.splitlines()
        self.assertTrue(lines[0].endswith("/jobs-root/jobs/work/myproj"), r.stderr)
        self.assertEqual(lines[1], "/opt/custom/bin 1")
        self.assertTrue((self.home / "jobs-root/bin/compute.py").exists())

    def test_auto_overflows_only_a_synced_job_when_local_slots_are_busy(self):
        holder = self.popen("run", "--class", "heavy", "--", "sleep", "4")
        time.sleep(0.8)
        r = self.compute("run", "--class", "heavy", "--sync", str(self.proj), "--", "sh", "-c", "echo $COMPUTE_HOST")
        self.assertEqual(r.stdout.strip(), HOST)
        local = self.compute("run", "--class", "heavy", "--", "sh", "-c", "echo $COMPUTE_HOST")
        self.assertEqual(local.stdout.strip(), "local")
        self.assertIn("queued behind 1 jobs", local.stderr)
        holder.wait(timeout=10)

    def test_a_job_running_remotely_does_not_block_the_local_queue(self):
        holder = self.popen("run", "--class", "heavy", "--", "sleep", "3")
        time.sleep(0.8)
        x = self.popen("run", "--class", "heavy", "--sync", str(self.proj), "--", "sleep", "6")  # overflows
        time.sleep(2)
        t0 = time.time()
        y = self.compute("run", "--class", "heavy", "--", "echo", "y", timeout=30)
        holder.wait(timeout=10)
        self.assertEqual((y.returncode, y.stdout.strip()), (0, "y"))
        self.assertLess(time.time() - t0, 5.5)
        self.assertIsNone(x.poll())
        x.wait(timeout=20)

    def test_remote_slots_hold_two_heavy_jobs_and_wait_status_is_not_repeated(self):
        jobs = [self.popen("run", "--class", "heavy", "--where", HOST, "--sync", str(self.proj), "--name", f"d{i}",
                           "--", "sleep", "3") for i in range(2)]
        holder = self.popen("run", "--class", "heavy", "--", "sleep", "3")
        time.sleep(2)
        pools = json.loads(self.compute("status", "--json").stdout)["hosts"][HOST]["pools"]["shared"]
        self.assertEqual(pools["free"], 0)
        q = self.compute("run", "--class", "heavy", "--sync", str(self.proj), "--", "true", timeout=30)
        self.assertLessEqual(q.stderr.count("queued behind"), 1)
        self.assertLessEqual(q.stderr.count("slots busy"), 1)
        for p in jobs + [holder]:
            p.wait(timeout=15)

    def test_unreachable_host_falls_back_to_the_local_queue_unless_forbidden(self):
        r = self.compute("run", "--class", "heavy", "--where", HOST, "--sync", str(self.proj), "--",
                         "sh", "-c", "echo $COMPUTE_HOST", ssh=self.bad)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "local"))
        self.assertIn("unreachable", r.stderr)
        r = self.compute("run", "--class", "heavy", "--where", HOST, "--no-fallback", "--sync", str(self.proj), "--",
                         "true", ssh=self.bad)
        self.assertEqual(r.returncode, C.EXIT_BROKER)
        status = self.compute("status", ssh=self.bad)
        self.assertEqual(status.returncode, 0)
        self.assertIn("unreachable", status.stdout)

    def test_ctrl_c_stops_the_remote_job_and_frees_its_units(self):
        pidfile = Path(self.tmp.name) / "pid"
        p = self.popen("run", "--class", "heavy", "--where", HOST, "--sync", str(self.proj), "--",
                       "sh", "-c", f"echo $$ > {pidfile}; sleep 120")
        pid = int(wait_for(pidfile))
        p.send_signal(signal.SIGINT)
        p.wait(timeout=30)
        self.assertEqual(p.returncode, 128 + signal.SIGINT)
        end = time.time() + 10
        while C.pid_alive(pid) and time.time() < end:
            time.sleep(0.1)
        self.assertFalse(C.pid_alive(pid))
        self.assertEqual(self.pool("shared", 4, remote=True).free_units(), 4)

    def test_a_dead_client_connection_stops_the_remote_job(self):
        pidfile = Path(self.tmp.name) / "pid2"
        p = self.popen("run", "--class", "moderate", "--where", HOST, "--sync", str(self.proj), "--",
                       "sh", "-c", f"echo $$ > {pidfile}; sleep 120")
        pid = int(wait_for(pidfile))
        p.kill()  # no client-side cleanup runs; the helper must notice the closed stdin itself
        end = time.time() + 10
        while C.pid_alive(pid) and time.time() < end:
            time.sleep(0.1)
        self.assertFalse(C.pid_alive(pid))


class BundleCarriesComputeSettings(ComputeCase):
    def test_a_bundle_built_with_a_private_profile_schedules_with_its_settings(self):
        spec = importlib.util.spec_from_file_location("dsstack_cli", ROOT / "scripts/dsstack.py")
        ds = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ds)
        policy = Path(self.tmp.name) / "policy"
        policy.mkdir()
        (policy / "resource-profile.json").write_text(json.dumps({"compute": {
            "local": {"slots": {"shared": 3}}, "hosts": {HOST: {"python": sys.executable}}}}))
        dest = Path(self.tmp.name) / "bundle"
        ds.bundle(ROOT, dest, policy, apply=True)
        env = {k: v for k, v in self.env.items() if k != "COMPUTE_PROFILE"}
        env["COMPUTE_SSH"] = self.bad
        out = subprocess.run([sys.executable, "-B", str(dest / "skills/ds-resources/scripts/compute.py"), "status", "--json"],
                             env=env, capture_output=True, text=True)
        status = json.loads(out.stdout)
        self.assertEqual(status["local"]["pools"]["shared"]["units"], 3)
        self.assertEqual(list(status["hosts"]), [HOST])
        self.assertTrue(status["hosts"][HOST]["unreachable"])


def snap(name, load, cpus, speed=1.0, free=6, units=6, arch="arm64", recent=0.0, reserve=0, measuring=None, down=False,
         jobs=None, local=None):
    """A host snapshot with pinned numbers, as the planner sees it."""
    jobs = jobs or ({"heavy": 10, "moderate": 4, "light": 2} if name == "local" else {"heavy": 12, "moderate": 6, "light": 2})
    return {"name": name, "local": name == "local" if local is None else local, "down": down, "cpus": cpus, "load1": load,
            "recent_threads": recent, "norm_load": (load + recent) / cpus, "arch": arch, "speed": speed,
            "speed_source": "profile", "pools": {"shared": {"units": units, "free": free}}, "running": [],
            "measuring": measuring, "max_norm_load": None, "reserve": reserve, "jobs": jobs,
            "classes": {"heavy": ["shared", 2], "moderate": ["shared", 1]}}


def rank(snaps, cls="moderate", latency=None, arch="any", work=None, sync=None, bal=None):
    bal = bal or C.default_balance()
    latency = latency or ("batch" if cls == "heavy" else "interactive")
    job = {"class": cls, "latency": latency, "arch": arch, "work": work or bal["work_seconds"][cls], "sync": sync or {}}
    return C.rank_hosts(job, snaps, bal)


def first(result):
    return result["order"][0]["host"] if result["order"] else None


class PlacementTests(unittest.TestCase):
    """The ranking function with fake loads: M2 = speed 1.0 per core, the older Intel host = 0.45 per thread."""

    def test_busy_but_less_loaded_fast_host_beats_a_swamped_slow_one(self):
        r = rank([snap("local", 15, 12), snap("mbp", 100, 16, speed=0.45, free=4, units=4)], "heavy")
        self.assertEqual(first(r), "local")

    def test_idle_hosts_tie_goes_to_the_faster_local_machine(self):
        for cls in ("moderate", "heavy"):
            r = rank([snap("local", 0, 12), snap("mbp", 0, 16, speed=0.45, free=4, units=4)], cls)
            self.assertEqual(first(r), "local")

    def test_slow_host_gets_work_only_when_it_finishes_sooner(self):
        slow_idle = snap("mbp", 0, 16, speed=0.45, free=4, units=4)
        self.assertEqual(first(rank([snap("local", 60, 12), slow_idle])), "mbp")      # local swamped
        self.assertEqual(first(rank([snap("local", 14, 12), slow_idle])), "local")    # local merely busy

    def test_small_jobs_pay_the_sync_cost(self):
        local, remote = snap("local", 20, 12), snap("mbp", 0, 16, speed=0.45, free=4, units=4)
        tiny = rank([local, remote], "light", work=5, sync={"mbp": 10})
        self.assertEqual(first(tiny), "local")
        free_sync = rank([local, remote], "light", work=5, sync={"mbp": 0.1})
        self.assertGreater(free_sync["order"][0]["finish"], 0)
        big = rank([snap("local", 40, 12), remote], "moderate", work=300, sync={"mbp": 10})
        self.assertEqual(first(big), "mbp")

    def test_batch_work_keeps_off_the_interactive_reserve_but_interactive_does_not(self):
        local = snap("local", 3, 12, free=3, reserve=2)  # a heavy job (2 units) would leave 1 < reserve
        remote = snap("mbp", 0, 16, speed=0.45, free=4, units=4)
        self.assertEqual(first(rank([local, remote], "heavy", latency="batch")), "mbp")
        self.assertEqual(first(rank([local, remote], "heavy", latency="interactive")), "local")
        self.assertEqual(first(rank([snap("local", 3, 12, free=6, reserve=2), remote], "heavy", latency="batch")), "local")

    def test_reserve_is_waived_when_the_other_host_is_far_slower_or_absent(self):
        local = snap("local", 3, 12, free=3, reserve=2)
        crawling = snap("mbp", 400, 16, speed=0.45, free=4, units=4)
        self.assertEqual(first(rank([local, crawling], "heavy", latency="batch")), "local")
        self.assertEqual(first(rank([local], "heavy", latency="batch")), "local")
        down = snap("mbp", 0, 16, speed=0.45, free=4, units=4, down=True)
        self.assertEqual(first(rank([local, down], "heavy", latency="batch")), "local")

    def test_batch_waits_rather_than_taking_reserved_units_while_the_other_host_is_merely_full(self):
        local = snap("local", 3, 12, free=3, reserve=2)
        full = snap("mbp", 0, 16, speed=0.45, free=0, units=4)
        r = rank([local, full], "heavy", latency="batch")
        self.assertEqual(r["order"], [])
        self.assertFalse(r["local_contending"])  # held back, so not ahead of anyone in the local queue
        self.assertEqual({o["host"]: o["why"] for o in r["options"]}, {"local": "reserved", "mbp": "full"})

    def test_arch_pin_only_allows_matching_hosts_even_if_slower(self):
        local, remote = snap("local", 0, 12), snap("mbp", 50, 16, speed=0.45, free=4, units=4, arch="x86_64")
        self.assertEqual(first(rank([local, remote], arch="x86_64")), "mbp")
        self.assertEqual(first(rank([local, remote], arch="arm64")), "local")
        r = rank([local, remote], arch="x86_64")
        self.assertEqual({o["host"]: o["why"] for o in r["options"]}, {"local": "arch", "mbp": None})
        self.assertFalse(r["local_contending"])  # a job pinned elsewhere must not hold up the local queue

    def test_measurement_window_and_unreachable_hosts_are_skipped_not_global(self):
        local = snap("local", 0, 12, measuring={"reason": "bench"})
        remote = snap("mbp", 0, 16, speed=0.45, free=4, units=4)
        self.assertEqual(first(rank([local, remote])), "mbp")
        self.assertEqual(first(rank([snap("local", 0, 12), snap("mbp", 0, 16, down=True, free=4, units=4)])), "local")
        both = rank([local, snap("mbp", 0, 16, free=4, units=4, measuring={"reason": "x"})])
        self.assertEqual(both["order"], [])
        ignored = C.rank_hosts({"class": "moderate", "latency": "interactive", "arch": "any", "work": 60, "sync": {},
                                "ignore_measure": True}, [local], C.default_balance())
        self.assertEqual(first(ignored), "local")

    def test_saturated_hosts_leave_the_job_queued(self):
        r = rank([snap("local", 0, 12, free=0), snap("mbp", 0, 16, free=0, units=4)], "heavy")
        self.assertEqual(r["order"], [])
        self.assertTrue(r["local_contending"])

    def test_recently_started_jobs_count_before_the_load_average_catches_up(self):
        a, b = snap("local", 5, 12), snap("local", 5, 12, recent=30)
        self.assertLess(rank([a])["order"][0]["finish"], rank([b])["order"][0]["finish"])
        remote = snap("mbp", 0, 16, speed=0.45, free=4, units=4)
        self.assertEqual(first(rank([b, remote], "moderate", work=300)), "mbp")

    def test_max_norm_load_takes_a_host_out(self):
        loaded = snap("local", 30, 12)
        loaded["max_norm_load"] = 2.0
        r = rank([loaded, snap("mbp", 0, 16, speed=0.45, free=4, units=4)])
        self.assertEqual(first(r), "mbp")

    def test_calibrated_speed_is_used_only_for_auto(self):
        calib = {"local": {"score": 2000.0}, "mbp": {"score": 900.0}}
        self.assertEqual(C.resolve_speed({"speed": "auto"}, "mbp", calib), (0.45, "calibrated"))
        self.assertEqual(C.resolve_speed({"speed": 0.5}, "mbp", calib), (0.5, "profile"))
        self.assertEqual(C.resolve_speed({"speed": "auto"}, "mbp", {})[0], 1.0)

    def test_recent_threads_decay_over_the_window(self):
        now = time.time()
        bal = C.default_balance()
        fresh = C.recent_threads([{"threads": 10, "start": now}], bal, now)
        older = C.recent_threads([{"threads": 10, "start": now - 45}], bal, now)
        gone = C.recent_threads([{"threads": 10, "start": now - 200}], bal, now)
        self.assertAlmostEqual(fresh, 10, places=1)
        self.assertAlmostEqual(older, 5, places=1)
        self.assertEqual(gone, 0)


@unittest.skipUnless(shutil.which("rsync"), "rsync is required")
class BalancingTests(ComputeCase):
    def host_of(self, *extra, cls="moderate"):
        r = self.compute("run", "--class", cls, *extra, "--", "sh", "-c", "echo $COMPUTE_HOST")
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip(), r

    def test_auto_sends_the_job_to_the_less_loaded_host_and_logs_why(self):
        self.set_loads(15, 100)
        where, r = self.host_of("--sync", str(self.proj))
        self.assertEqual(where, "local")
        self.assertIn("placement:", r.stderr)
        self.set_loads(80, 0)
        where, _ = self.host_of("--sync", str(self.proj))
        self.assertEqual(where, HOST)
        status = self.compute("status").stdout
        self.assertIn("recent placements", status)
        self.assertIn("-> builder", status)

    def test_batch_leaves_the_local_reserve_free_for_interactive_work(self):
        self.write_profile({"local": {"slots": {"shared": 4}, "interactive_reserve": 2},
                            "hosts": {HOST: {"python": sys.executable, "speed": 0.45, "slots": {"shared": 4}}},
                            "default_host": HOST})
        holder = self.popen("run", "--class", "moderate", "--", "sleep", "3")
        time.sleep(0.8)  # 3 of 4 units free; a heavy job would take 2 and leave 1 < reserve
        where, _ = self.host_of("--sync", str(self.proj), cls="heavy")
        self.assertEqual(where, HOST)
        where, _ = self.host_of("--sync", str(self.proj), "--latency", "interactive", cls="heavy")
        self.assertEqual(where, "local")
        holder.wait(timeout=10)

    def test_arch_pins_hosts_for_every_class_and_needs_sync_to_leave_local(self):
        self.assertEqual(self.host_of("--sync", str(self.proj), "--arch", "x86_64")[0], HOST)
        self.assertEqual(self.host_of("--sync", str(self.proj), "--arch", "x86_64", cls="light")[0], HOST)
        self.assertEqual(self.host_of("--sync", str(self.proj), "--arch", "arm64")[0], "local")
        self.assertEqual(self.host_of("--where", HOST, "--sync", str(self.proj), "--arch", "x86_64")[0], HOST)
        r = self.compute("run", "--class", "moderate", "--arch", "x86_64", "--", "true")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--sync", r.stderr)
        r = self.compute("run", "--class", "moderate", "--where", HOST, "--sync", str(self.proj), "--arch", "arm64", "--", "true")
        self.assertEqual(r.returncode, 2)

    def test_a_job_pinned_elsewhere_does_not_hold_up_the_local_queue(self):
        holder = self.popen("run", "--class", "heavy", "--", "sleep", "3")
        time.sleep(0.8)
        remote_job = self.popen("run", "--class", "heavy", "--sync", str(self.proj), "--arch", "x86_64", "--", "sleep", "5")
        time.sleep(1.5)
        t0 = time.time()
        y = self.compute("run", "--class", "heavy", "--", "echo", "y", timeout=30)
        self.assertEqual((y.returncode, y.stdout.strip()), (0, "y"))
        self.assertLess(time.time() - t0, 3.5)
        holder.wait(timeout=10)
        remote_job.wait(timeout=20)

    def test_local_measurement_drains_one_host_and_auto_uses_the_other(self):
        self.assertEqual(self.compute("measure", "begin", "--host", "local", "--reason", "m2 bench").returncode, 0)
        where, _ = self.host_of("--sync", str(self.proj))
        self.assertEqual(where, HOST)
        # without --sync there is nowhere else to go, so the job waits for the window
        q = self.popen("run", "--class", "moderate", "--", "echo", "after")
        time.sleep(1)
        self.assertIsNone(q.poll())
        self.compute("measure", "end", "--host", "local")
        out, err = q.communicate(timeout=15)
        self.assertIn("after", out)
        self.assertIn("measurement window", err)

    def test_measure_wait_and_status_see_locks_from_pools_the_profile_no_longer_defines(self):
        slots = self.state / "slots"
        slots.mkdir()
        (slots / "heavy.0.info").write_text(json.dumps({"id": "old", "class": "heavy", "project": "p", "pid": 1,
                                                        "start": time.time(), "cmd": "old job"}))
        code = ("import fcntl,os,sys,time;fd=os.open(sys.argv[1],os.O_CREAT|os.O_RDWR);"
                "fcntl.flock(fd,fcntl.LOCK_EX);print('held',flush=True);time.sleep(30)")
        holder = subprocess.Popen([sys.executable, "-c", code, str(slots / "heavy.0.lock")], stdout=subprocess.PIPE, text=True)
        self.procs.append(holder)
        holder.stdout.readline()
        status = json.loads(self.compute("status", "--json").stdout)
        self.assertEqual(len([h for h in status["local"]["pools"]["heavy"]["holders"] if h]), 1)
        r = self.compute("measure", "begin", "--host", "local", "--wait", "2")
        self.assertNotIn("host drained", r.stdout)
        self.assertEqual(r.returncode, 3)
        self.compute("measure", "end", "--host", "local")

    def test_balance_lists_per_host_load_and_the_placement_it_would_make(self):
        self.set_loads(15, 100)
        out = self.compute("balance").stdout
        self.assertIn("normalized 1.25", out)
        self.assertIn("normalized 6.25", out)
        self.assertIn("heavy/batch: local", out)
        data = json.loads(self.compute("balance", "--json").stdout)
        self.assertEqual(data["hosts"]["local"]["cpus"], 12)
        self.assertEqual({p["class"] + "/" + p["latency"]: p["chosen"] for p in data["plan"]}["moderate/interactive"], "local")

    def test_old_pool_format_in_the_profile_fails_with_a_clear_message(self):
        self.profile.write_text(json.dumps({"compute": {"local": {"slots": {"heavy": 1, "moderate": 2}}}}))
        r = self.compute("status")
        self.assertEqual(r.returncode, C.EXIT_BROKER)
        self.assertIn("old separate heavy/moderate pools", r.stderr)

    def test_calibrate_records_scores_and_auto_speed_uses_them(self):
        r = self.compute("calibrate", "--seconds", "0.2", timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        calib = json.loads((self.state / "calibration.json").read_text())
        self.assertEqual(sorted(calib), ["builder", "local"])
        self.write_profile({"local": {"speed": 1.0}, "hosts": {HOST: {"python": sys.executable, "speed": "auto"}},
                            "default_host": HOST})
        data = json.loads(self.compute("balance", "--json").stdout)
        self.assertEqual(data["hosts"][HOST]["speed_source"], "calibrated")


if __name__ == "__main__":
    unittest.main()
