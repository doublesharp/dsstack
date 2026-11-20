#!/usr/bin/env python3
"""compute: a small compute broker that shares heavy work between this machine and an optional second one.

Local slots are flock-based semaphores under a state directory. Portable jobs
(those given --sync DIR) can overflow to a remote host over ssh/rsync, where the
same file runs as a helper (`compute.py _remote ...`) that owns the remote slot,
the job and its cleanup. With no remote host configured it is a local scheduler.

Settings come from the `compute` section of the skill's resource profile
(profiles/default.json, or the file named by COMPUTE_PROFILE); see
references/compute.md. Nothing machine-specific lives in this file.

Locks are kernel flocks, so a crashed holder frees its slot automatically; the
JSON sidecars next to each lock only describe the holder for `compute status`.
Python 3.9+, standard library only (the same file is copied to the remote host).
"""
from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import json
import os
import re
import select
import shlex
import signal
import subprocess
import sys
import threading
import time

VERSION = 1
CLASSES = ("heavy", "moderate", "light")
EXIT_BROKER = 125
EXIT_BUSY, EXIT_MEASURING, EXIT_DIRBUSY, EXIT_ABORTED = 75, 76, 77, 78
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
SKILL_PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "profiles", "default.json")


def default_config() -> dict:
    cpus = os.cpu_count() or 4
    return {
        "state": None,
        "default_host": None,
        "hosts": {},
        "local": {
            "slots": {"heavy": 1, "moderate": 2},
            "jobs": {"heavy": cpus, "moderate": max(2, cpus // 3), "light": 2},
        },
        "poll_seconds": 0.5,
        "remote_poll_seconds": 5,
    }


def default_host(entry: dict) -> dict:
    """Remote defaults: one shared pool where heavy takes the whole host and moderate takes half."""
    base = {
        "ssh": None, "python": "python3", "root": "~/compute", "env_dir": None,
        "slots": {"shared": 2}, "classes": {"heavy": ["shared", 2], "moderate": ["shared", 1]},
        "jobs": {"heavy": 8, "moderate": 4, "light": 2},
        "measure_marker": "~/compute/MEASURING", "path_prepend": ["~/.cargo/bin"],
        "busy_pattern": "Runner.Worker", "pause_commands": [], "resume_commands": [],
    }
    base.update(entry)
    base["ssh"] = base["ssh"] or entry.get("name")
    return base


# Rsync excludes applied to every --sync. Add more per project with a
# `.compute-sync` file in DIR (rsync filter rules, one per line, `+ pat` or
# `- pat`, applied before these) or with --include/--exclude.
DEFAULT_EXCLUDES = [
    "target/", "node_modules/", ".git/", ".cargo-targets/", "/build/", "/out/",
    "/cache/", "/dist/", "/reports/", "/tmp/", ".venv/", "__pycache__/",
    ".pytest_cache/", ".DS_Store", ".next/", ".turbo/",
]


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def log(msg: str) -> None:
    print(f"[compute] {msg}", file=sys.stderr, flush=True)


def die(msg: str, code: int = EXIT_BROKER) -> "None":
    log(msg)
    raise SystemExit(code)


def _profile_path() -> str:
    return os.environ.get("COMPUTE_PROFILE") or SKILL_PROFILE


def load_config() -> dict:
    """Defaults, overlaid by the `compute` section of the resource profile."""
    cfg = default_config()
    path = _profile_path()
    explicit = bool(os.environ.get("COMPUTE_PROFILE"))
    profile = {}
    if explicit or os.path.exists(path):
        try:
            with open(path) as fh:
                profile = json.load(fh)
        except (OSError, ValueError) as exc:
            die(f"bad resource profile {path}: {exc}")
    user = profile.get("compute", {}) if isinstance(profile, dict) else {}
    if not isinstance(user, dict):
        die(f"profile {path}: compute must be an object")
    allowed = {"state", "default_host", "hosts", "local", "poll_seconds", "remote_poll_seconds"}
    if user.keys() - allowed:
        die(f"profile {path}: unknown compute fields {sorted(user.keys() - allowed)}")
    for key in ("state", "default_host", "poll_seconds", "remote_poll_seconds"):
        if key in user:
            cfg[key] = user[key]
    if "local" in user:
        for key in ("slots", "jobs"):
            cfg["local"][key].update(user["local"].get(key, {}))
    for name, entry in user.get("hosts", {}).items():
        safe_name(name, "host")
        cfg["hosts"][name] = default_host(dict(entry, name=name))
    if cfg["default_host"] is None and len(cfg["hosts"]) == 1:
        cfg["default_host"] = next(iter(cfg["hosts"]))
    if cfg["default_host"] is not None and cfg["default_host"] not in cfg["hosts"]:
        die(f"profile {path}: default_host {cfg['default_host']!r} is not in compute.hosts")
    for h in cfg["hosts"].values():
        h["pools"], h["class_pool"] = h["slots"], h["classes"]
        h["env_dir"] = h["env_dir"] or h["root"].rstrip("/") + "/env"
    cfg["local"]["pools"] = cfg["local"]["slots"]
    cfg["local"]["class_pool"] = {"heavy": ["heavy", 1], "moderate": ["moderate", 1]}
    cfg["profile_path"] = path
    cfg["scratch"] = profile.get("scratch") if isinstance(profile, dict) else None
    cfg["require_mount"] = profile.get("require_mount", True) if isinstance(profile, dict) else True
    return cfg


def state_root(cfg: dict) -> str:
    """COMPUTE_STATE, then compute.state, then <profile scratch>/.compute, then the user's state dir."""
    env = os.environ.get("COMPUTE_STATE")
    if env:
        return env
    if cfg["state"]:
        return os.path.expanduser(cfg["state"])
    if cfg["scratch"]:
        return os.path.join(os.path.expanduser(cfg["scratch"]), ".compute")
    base = os.environ.get("XDG_STATE_HOME") or os.path.join(os.path.expanduser("~"), ".local", "state")
    return os.path.join(base, "dsstack", "compute")


def ensure_state(root: str, cfg: dict) -> None:
    scratch = cfg["scratch"] and os.path.expanduser(cfg["scratch"])
    if scratch and not os.environ.get("COMPUTE_STATE") and not cfg["state"]:
        if not os.path.isdir(scratch) or (cfg["require_mount"] and not os.path.ismount(scratch)):
            die(f"output root {scratch} is unavailable; refusing to use another disk")
    os.makedirs(root, exist_ok=True)


def atomic_write(path: str, data: dict | str) -> None:
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w") as fh:
        fh.write(data if isinstance(data, str) else json.dumps(data))
    os.replace(tmp, path)


def read_json(path: str):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def safe_name(value: str, what: str) -> str:
    if not isinstance(value, str) or not NAME_RE.match(value) or value in (".", ".."):
        raise ValueError(f"unsafe {what} name {value!r}: use letters, digits, . _ - only")
    return value


def fmt_secs(sec: float) -> str:
    sec = int(sec)
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec // 60}m{sec % 60:02d}s"
    return f"{sec // 3600}h{(sec % 3600) // 60:02d}m"


def uptime_line() -> str:
    try:
        out = subprocess.run(["uptime"], capture_output=True, text=True, timeout=5).stdout
        return out.strip()
    except Exception as exc:  # pragma: no cover
        return f"unavailable ({exc})"


def pid_alive(pid) -> bool:
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except (PermissionError, ValueError, TypeError):
        return True
    return True


# --------------------------------------------------------------------------
# flock pools (used locally and, via the helper, on the remote host)
# --------------------------------------------------------------------------

class Lease:
    def __init__(self, pool: "Pool", units: list[tuple[int, int]], info: dict):
        self.pool, self.units, self.info = pool, units, info

    @property
    def fds(self) -> list[int]:
        return [fd for _, fd in self.units]

    @property
    def label(self) -> str:
        return ",".join(f"{self.pool.name}.{i}" for i, _ in self.units)

    def release(self) -> None:
        for i, fd in self.units:
            try:
                os.unlink(self.pool.info_path(i))
            except OSError:
                pass
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)  # frees every inherited copy too
            except OSError:
                pass
            try:
                os.close(fd)
            except OSError:
                pass
        self.units = []


class Pool:
    def __init__(self, root: str, name: str, units: int):
        self.root, self.name, self.units = root, name, int(units)
        os.makedirs(root, exist_ok=True)

    def lock_path(self, i: int) -> str:
        return os.path.join(self.root, f"{self.name}.{i}.lock")

    def info_path(self, i: int) -> str:
        return os.path.join(self.root, f"{self.name}.{i}.info")

    def try_acquire(self, weight: int, info: dict, inheritable: bool = True) -> Lease | None:
        weight = min(weight, self.units)
        mutex = os.open(os.path.join(self.root, f"{self.name}.mutex"), os.O_CREAT | os.O_RDWR, 0o644)
        try:
            fcntl.flock(mutex, fcntl.LOCK_EX)
            got: list[tuple[int, int]] = []
            for i in range(self.units):
                fd = os.open(self.lock_path(i), os.O_CREAT | os.O_RDWR, 0o644)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    os.close(fd)
                    continue
                got.append((i, fd))
                if len(got) == weight:
                    break
            if len(got) < weight:
                for _, fd in got:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
                return None
            for i, fd in got:
                os.set_inheritable(fd, inheritable)
                atomic_write(self.info_path(i), dict(info, unit=i, units=[u for u, _ in got]))
            return Lease(self, got, info)
        finally:
            fcntl.flock(mutex, fcntl.LOCK_UN)
            os.close(mutex)

    def holders(self) -> list[dict | None]:
        """Per-unit state: None when free, else the holder's info (flock-verified)."""
        out: list[dict | None] = []
        for i in range(self.units):
            fd = os.open(self.lock_path(i), os.O_CREAT | os.O_RDWR, 0o644)
            try:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    out.append(read_json(self.info_path(i)) or {"unknown": True})
                    continue
                fcntl.flock(fd, fcntl.LOCK_UN)
                out.append(None)  # any sidecar left here is a crashed holder's; it is ignored
            finally:
                os.close(fd)
        return out

    def free_units(self) -> int:
        return sum(1 for h in self.holders() if h is None)


# --------------------------------------------------------------------------
# waiter queue (local FIFO per class); liveness == waiter holds a flock
# --------------------------------------------------------------------------

class Waiter:
    def __init__(self, root: str, cls: str, info: dict):
        self.dir = os.path.join(root, "queue", cls)
        os.makedirs(self.dir, exist_ok=True)
        self.path = os.path.join(self.dir, f"{time.time_ns():020d}-{os.getpid()}.json")
        self.fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o644)
        fcntl.flock(self.fd, fcntl.LOCK_EX)
        atomic_write_fd(self.fd, json.dumps(info))

    def ahead(self) -> int:
        n = 0
        for name in sorted(os.listdir(self.dir)):
            full = os.path.join(self.dir, name)
            if full == self.path:
                return n
            if waiter_alive(full):
                n += 1
        return n

    def close(self) -> None:
        try:
            os.unlink(self.path)
        except OSError:
            pass
        try:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
        except OSError:
            pass


def atomic_write_fd(fd: int, text: str) -> None:
    os.ftruncate(fd, 0)
    os.pwrite(fd, text.encode(), 0)


def waiter_alive(path: str) -> bool:
    try:
        fd = os.open(path, os.O_RDWR)
    except OSError:
        return False
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return True
        # Unlocked: dead waiter. Give a just-created file a moment before pruning.
        try:
            if time.time() - os.fstat(fd).st_mtime > 5:
                os.unlink(path)
                return False
        except OSError:
            return False
        return True
    finally:
        os.close(fd)


def list_waiters(root: str, cls: str) -> list[dict]:
    d = os.path.join(root, "queue", cls)
    out = []
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        full = os.path.join(d, name)
        if waiter_alive(full):
            info = read_json(full) or {}
            out.append(info)
    return out


# --------------------------------------------------------------------------
# measurement windows
# --------------------------------------------------------------------------

def local_marker_path(root: str, host: str) -> str:
    return os.path.join(root, "measure", f"{host}.json")


def measuring(root: str, host: str) -> dict | None:
    return read_json(local_marker_path(root, host))


# --------------------------------------------------------------------------
# project / directory naming
# --------------------------------------------------------------------------

def derive_names(sync_dir: str, project: str | None, name: str | None) -> tuple[str, str]:
    d = os.path.realpath(sync_dir)
    home = os.path.expanduser("~")
    ws = os.path.join(home, "Workspaces")
    wt = os.path.join(ws, "worktrees")
    p, n = project, name
    if d.startswith(wt + os.sep):
        parts = d[len(wt) + 1:].split(os.sep)
        p = p or parts[0]
        n = n or ("-".join(parts[1:]) or parts[0])
    elif d.startswith(ws + os.sep):
        parts = d[len(ws) + 1:].split(os.sep)
        p = p or parts[0]
        n = n or ("-".join(parts[1:]) or parts[0])
    else:
        p = p or os.environ.get("COMPUTE_PROJECT") or os.path.basename(os.path.dirname(d)) or "adhoc"
        n = n or os.path.basename(d)
    return safe_name(p, "project"), safe_name(n, "dir")


# --------------------------------------------------------------------------
# remote helper (runs on the remote host as `compute.py _remote <cmd>`)
# --------------------------------------------------------------------------

def self_hash() -> str:
    with open(os.path.abspath(__file__), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _rhome() -> str:
    return os.path.expanduser("~")


_RROOT = ["~/compute"]  # set per request by cmd_remote


def _rbase() -> str:
    return os.path.abspath(os.path.expanduser(_RROOT[0]))


def _expand(path: str) -> str:
    return os.path.expanduser(path)


def remote_probe(req: dict) -> dict:
    base = _rbase()
    out: dict = {"hash": self_hash(), "home": _rhome(), "pools": {}, "running": []}
    pattern = req.get("busy_pattern") or ""
    for pname, units in req.get("pools", {}).items():
        pool = Pool(os.path.join(base, "slots"), pname, units)
        holders = pool.holders()
        out["pools"][pname] = {"units": units, "free": sum(1 for h in holders if h is None)}
        seen = set()
        for h in holders:
            if h and h.get("id") not in seen:
                seen.add(h.get("id"))
                out["running"].append(h)
    marker = req.get("marker")
    out["measuring"] = read_json(_expand(marker)) if marker else None
    out["load"] = uptime_line()
    try:
        ps = subprocess.run(["ps", "-axo", "pid,user,command"], capture_output=True, text=True, timeout=10).stdout
        out["ci_workers"] = [ln.strip()[:160] for ln in ps.splitlines() if pattern and pattern in ln]
    except Exception:
        out["ci_workers"] = []
    return out


def remote_measure(req: dict) -> dict:
    marker = _expand(req["marker"])
    action = req["action"]
    if action == "begin":
        os.makedirs(os.path.dirname(marker), exist_ok=True)
        existing = read_json(marker)
        if existing and not req.get("force"):
            return {"ok": False, "existing": existing}
        atomic_write(marker, req["info"])
        return {"ok": True}
    if action == "end":
        try:
            os.unlink(marker)
        except FileNotFoundError:
            pass
        return {"ok": True}
    return {"ok": False, "error": "bad action"}


def remote_result(req: dict) -> dict:
    rec = read_json(os.path.join(_rbase(), "runs", safe_name(req["id"], "id") + ".json"))
    if not rec:
        return {"state": "unknown"}
    if rec.get("state") == "running" and not pid_alive(rec.get("pid")):
        return {"state": "unknown", "note": "helper gone without result"}
    return rec


def remote_kill(req: dict) -> dict:
    rec = read_json(os.path.join(_rbase(), "runs", safe_name(req["id"], "id") + ".json"))
    if rec and rec.get("state") == "running" and pid_alive(rec.get("pid")):
        os.kill(int(rec["pid"]), signal.SIGTERM)
        return {"killed": True}
    return {"killed": False}


def kill_group(proc: subprocess.Popen, sig=signal.SIGTERM, grace: float = 10.0) -> None:
    """Signal a job's process group; escalate to SIGKILL after `grace` seconds."""
    try:
        os.killpg(proc.pid, sig)
    except (ProcessLookupError, PermissionError):
        return

    def reaper():
        end = time.time() + grace
        while time.time() < end:
            if proc.poll() is not None:
                return
            time.sleep(0.2)
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

    threading.Thread(target=reaper, daemon=True).start()


def remote_run(req: dict) -> int:
    """Acquire slot+dir, report READY, wait for GO, run the job. See protocol in the module docs."""
    def say(tag: str, payload: dict) -> None:
        sys.stdout.write(f"{tag} {json.dumps(payload)}\n")
        sys.stdout.flush()

    try:
        project = safe_name(req["project"], "project")
        dirname = safe_name(req["dir"], "dir")
        job_id = safe_name(req["id"], "id")
    except ValueError as exc:
        say("ERROR", {"error": str(exc)})
        return EXIT_BROKER
    base = _rbase()
    cls = req["class"]
    lease = None
    dirlock = None
    try:
        if cls != "light":
            pool = Pool(os.path.join(base, "slots"), req["pool"], req["units"])
            info = {"id": job_id, "project": project, "dir": dirname, "class": cls,
                    "cmd": req.get("cmd", ""), "pid": os.getpid(), "start": time.time(), "host": "remote"}
            lease = pool.try_acquire(int(req["weight"]), info, inheritable=False)
            if lease is None:
                say("BUSY", {"reason": "full", "running": [h for h in pool.holders() if h]})
                return EXIT_BUSY
            marker = req.get("marker")
            mk = read_json(_expand(marker)) if marker else None
            if mk and not req.get("ignore_measure"):
                say("BUSY", {"reason": "measuring", "marker": mk})
                return EXIT_MEASURING
        locks = os.path.join(base, "locks")
        os.makedirs(locks, exist_ok=True)
        dirlock = os.open(os.path.join(locks, f"{project}.{dirname}.lock"), os.O_CREAT | os.O_RDWR, 0o644)
        try:
            fcntl.flock(dirlock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            say("BUSY", {"reason": "dirbusy"})
            return EXIT_DIRBUSY
        jobdir = os.path.join(base, "jobs", project, dirname)
        tmpdir = os.path.join(base, "tmp", project, dirname)
        cargo = os.path.join(base, "cargo", project, dirname)
        for d in (jobdir, tmpdir, cargo, os.path.join(base, "runs")):
            os.makedirs(d, exist_ok=True)
        say("READY", {"jobdir": jobdir, "home": _rhome(), "slot": lease.label if lease else "light"})

        line = sys.stdin.readline()
        if line.strip() != "GO":
            return EXIT_ABORTED

        cwd = os.path.normpath(os.path.join(jobdir, req.get("cwd_rel") or "."))
        if not (cwd == jobdir or cwd.startswith(jobdir + os.sep)):
            say("ERROR", {"error": "cwd escapes job dir"})
            return EXIT_BROKER
        os.makedirs(cwd, exist_ok=True)
        env = dict(os.environ)
        env["PATH"] = ":".join([os.path.expanduser(p) for p in req.get("path_prepend", [])] + [env.get("PATH", "/usr/bin:/bin")])
        env.update({
            "COMPUTE_JOBS": str(req["jobs"]), "COMPUTE_CLASS": cls, "COMPUTE_HOST": req.get("host", "remote"),
            "COMPUTE_PROJECT": project, "COMPUTE_DIRNAME": dirname, "COMPUTE_JOBDIR": jobdir,
            "COMPUTE_SLOT": lease.label if lease else "light",
            "CARGO_TARGET_DIR": cargo, "TMPDIR": tmpdir,
        })
        env.setdefault("CARGO_BUILD_JOBS", str(req["jobs"]))
        envdir = _expand(req.get("env_dir") or os.path.join(base, "env"))
        env_files = [os.path.join(envdir, "default.sh"), os.path.join(envdir, project + ".sh")]
        wrapper = ('set -a; while [ "$1" != "--" ]; do [ -f "$1" ] && . "$1"; shift; done; '
                   'shift; set +a; exec "$@"')
        argv = ["/bin/bash", "-c", wrapper, "bash", *env_files, "--", *req["argv"]]

        runs = os.path.join(base, "runs", job_id + ".json")
        atomic_write(runs, {"state": "running", "pid": os.getpid(), "start": time.time()})
        try:
            proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, start_new_session=True)
        except OSError as exc:
            atomic_write(runs, {"state": "done", "rc": 127, "error": str(exc)})
            sys.stderr.write(f"compute: cannot start job: {exc}\n")
            return 127

        stop = {"sig": None}

        def on_signal(signum, _frame):
            stop["sig"] = signum
            kill_group(proc, signal.SIGTERM)

        for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(s, on_signal)

        def watch_stdin():  # EOF means the client went away (Ctrl-C, ssh death)
            try:
                while os.read(0, 4096):
                    pass
            except OSError:
                pass
            stop["sig"] = stop["sig"] or signal.SIGHUP
            kill_group(proc, signal.SIGTERM)

        threading.Thread(target=watch_stdin, daemon=True).start()
        rc = proc.wait()
        rc = 128 - rc if rc < 0 else rc
        atomic_write(runs, {"state": "done", "rc": rc, "end": time.time(), "killed_by": stop["sig"]})
        return rc
    finally:
        if lease:
            lease.release()
        if dirlock is not None:
            try:
                fcntl.flock(dirlock, fcntl.LOCK_UN)
                os.close(dirlock)
            except OSError:
                pass


def cmd_remote(argv: list[str]) -> int:
    sub = argv[0] if argv else ""
    if sub == "hash":
        print(self_hash())
        return 0
    req = json.loads(sys.stdin.readline() or "{}")
    _RROOT[0] = req.get("root", _RROOT[0])
    if sub == "run":
        return remote_run(req)
    handlers = {"probe": remote_probe, "measure": remote_measure, "result": remote_result, "kill": remote_kill}
    if sub in handlers:
        print(json.dumps(handlers[sub](req)))
        return 0
    print(f"unknown remote command {sub}", file=sys.stderr)
    return 2


# --------------------------------------------------------------------------
# remote client (runs on this machine)
# --------------------------------------------------------------------------

class Remote:
    def __init__(self, cfg: dict, host: str, root: str):
        self.cfg, self.host, self.root = cfg, host, root
        h = cfg["hosts"].get(host)
        if not h:
            die(f"unknown host {host!r}; configured: {', '.join(cfg['hosts'])}")
        self.h = h
        self.ssh_bin = os.environ.get("COMPUTE_SSH", "ssh")
        self.ssh_opts = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
                         "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4"]
        self.base = h["root"].rstrip("/")
        self.helper = self.base + "/bin/compute.py"
        self.ready = False

    def ssh_argv(self, remote_cmd: str) -> list[str]:
        return [self.ssh_bin, *self.ssh_opts, self.h["ssh"], remote_cmd]

    @staticmethod
    def rq(path: str) -> str:
        """Quote a remote path but keep a leading ~/ expandable by the remote shell."""
        return "~/" + shlex.quote(path[2:]) if path.startswith("~/") else shlex.quote(path)

    def helper_cmd(self, sub: str) -> str:
        return f"{shlex.quote(self.h['python'])} {self.rq(self.helper)} _remote {sub}"

    def req(self, **extra) -> dict:
        return {"root": self.base, "env_dir": self.h["env_dir"], **extra}

    def call(self, sub: str, req: dict, timeout: float = 30) -> dict | None:
        try:
            cp = subprocess.run(self.ssh_argv(self.helper_cmd(sub)), input=json.dumps(req) + "\n",
                                capture_output=True, text=True, timeout=timeout)
        except (subprocess.TimeoutExpired, OSError):
            return None
        if cp.returncode != 0:
            return None
        try:
            return json.loads(cp.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return None

    def ensure_helper(self) -> bool:
        if self.ready:
            return True
        mine = self_hash()
        try:
            cp = subprocess.run(self.ssh_argv(self.helper_cmd("hash")), capture_output=True, text=True, timeout=30)
        except (subprocess.TimeoutExpired, OSError):
            return False
        if cp.returncode == 0 and cp.stdout.strip() == mine:
            self.ready = True
            return True
        try:
            with open(os.path.abspath(__file__), "rb") as fh:
                data = fh.read()
            h = self.rq(self.helper)
            cp = subprocess.run(self.ssh_argv(f"mkdir -p {self.rq(self.base + '/bin')} && cat > {h}.new.$$ && mv {h}.new.$$ {h}"),
                                input=data, capture_output=True, timeout=60)
        except (subprocess.TimeoutExpired, OSError):
            return False
        self.ready = cp.returncode == 0
        return self.ready

    def probe(self) -> dict | None:
        if not self.ensure_helper():
            return None
        return self.call("probe", self.req(pools=self.h["pools"], marker=self.h.get("measure_marker"),
                                           busy_pattern=self.h.get("busy_pattern")))

    def rsync_e(self) -> str:
        return " ".join(shlex.quote(x) for x in [self.ssh_bin, *self.ssh_opts])

    def run_request(self, ctx: dict) -> dict:
        pool, weight = self.h["class_pool"].get(ctx["class"], [None, 0])
        return self.req(**{
            "id": ctx["id"], "project": ctx["project"], "dir": ctx["dirname"], "class": ctx["class"],
            "pool": pool, "units": self.h["pools"].get(pool, 0), "weight": weight,
            "argv": ctx["argv"], "cmd": ctx["cmd"], "cwd_rel": ctx.get("cwd_rel", "."),
            "jobs": self.h["jobs"].get(ctx["class"], 4), "host": self.host,
            "marker": self.h.get("measure_marker"), "ignore_measure": ctx.get("ignore_measure", False),
            "path_prepend": self.h.get("path_prepend", []),
        })


class RemoteInterrupted(Exception):
    pass


def sync_filters(sync_dir: str, includes: list[str], excludes: list[str]) -> list[str]:
    rules: list[str] = []
    for pat in includes:
        rules.append(f"--include={pat}")
    for pat in excludes:
        rules.append(f"--exclude={pat}")
    extra = os.path.join(sync_dir, ".compute-sync")
    if os.path.isfile(extra):
        with open(extra) as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    rules.append(f"--filter={line}")
    rules += [f"--exclude={pat}" for pat in DEFAULT_EXCLUDES]
    return rules


def run_remote(remote: Remote, ctx: dict, args) -> tuple[str, int, str]:
    """One remote attempt. Returns (status, rc, detail): status in ran|busy|unreachable|error."""
    if not remote.ensure_helper():
        return "unreachable", 0, "ssh/helper install failed"
    req = remote.run_request(ctx)
    proc = subprocess.Popen(remote.ssh_argv(remote.helper_cmd("run")), stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=False)
    interrupted = {"sig": None}
    old = {}

    def on_signal(signum, _frame):
        interrupted["sig"] = signum
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.terminate()
        except Exception:
            pass

    def abort_remote():
        remote.call("kill", remote.req(id=ctx["id"]), timeout=10)

    def read_line(timeout: float) -> str:
        end = time.time() + timeout
        buf = b""
        fd = proc.stdout.fileno()
        while time.time() < end and not buf.endswith(b"\n"):
            if interrupted["sig"]:
                raise RemoteInterrupted()
            r, _, _ = select.select([fd], [], [], 0.5)
            if r:
                ch = os.read(fd, 1)
                if not ch:
                    break
                buf += ch
        return buf.decode(errors="replace").strip()

    for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        old[s] = signal.signal(s, on_signal)
    try:
        try:
            proc.stdin.write((json.dumps(req) + "\n").encode())
            proc.stdin.flush()
            first = read_line(45)
        except (BrokenPipeError, OSError):
            first = ""
        if not first:
            proc.kill()
            proc.wait()
            return "unreachable", 0, "no response from remote helper"
        tag, _, payload = first.partition(" ")
        try:
            data = json.loads(payload) if payload else {}
        except ValueError:
            data = {}
        if tag == "BUSY":
            proc.wait()
            return "busy", 0, data.get("reason", "busy")
        if tag != "READY":
            proc.wait()
            return "error", EXIT_BROKER, f"remote said: {first[:200]}"
        jobdir = data["jobdir"]
        if ctx.get("on_ready"):
            ctx["on_ready"]()
        log(f"{ctx['host']}: slot {data.get('slot')} held; syncing")
        if ctx.get("sync_dir"):
            rc = rsync_up(remote, ctx, jobdir)
            if rc not in (0, 23, 24):
                proc.stdin.close()
                proc.wait()
                return "unreachable", 0, f"rsync failed (exit {rc})"
            if rc in (23, 24):
                log("rsync reported vanished/unreadable files (continuing)")
        try:
            proc.stdin.write(b"GO\n")
            proc.stdin.flush()
        except (BrokenPipeError, OSError):
            proc.wait()
            return "unreachable", 0, "connection lost before start"
        log(f"{ctx['host']}: running ({ctx['class']}, COMPUTE_JOBS={req['jobs']}) in {jobdir}")

        def pump():
            out = sys.stdout.buffer
            while True:
                chunk = proc.stdout.read1(65536)
                if not chunk:
                    return
                out.write(chunk)
                out.flush()

        t = threading.Thread(target=pump, daemon=True)
        t.start()
        while proc.poll() is None:
            if interrupted["sig"]:
                break
            time.sleep(0.1)
        if interrupted["sig"]:
            log("interrupted; stopping the remote job")
            abort_remote()
            try:
                proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                proc.kill()
            return "ran", 128 + interrupted["sig"], "interrupted"
        t.join(timeout=5)
        rc = proc.returncode
        if rc == 255:  # ssh itself failed after start: ask the remote what happened
            rc2, note = fetch_result(remote, ctx["id"])
            if rc2 is None:
                return "ran", 255, "connection lost; remote job outcome unknown"
            rc, detail = rc2, note
        else:
            detail = ""
        if ctx.get("artifacts"):
            fetch_artifacts(remote, ctx, jobdir)
        return "ran", rc, detail
    except RemoteInterrupted:
        abort_remote()
        try:
            proc.kill()
        except Exception:
            pass
        return "ran", 128 + (interrupted["sig"] or signal.SIGINT), "interrupted"
    finally:
        for s, h in old.items():
            signal.signal(s, h)


def fetch_result(remote: Remote, job_id: str) -> tuple[int | None, str]:
    for _ in range(6):
        rec = remote.call("result", remote.req(id=job_id), timeout=15)
        if rec and rec.get("state") == "done":
            return int(rec.get("rc", 255)), "ssh dropped; exit code recovered from remote"
        if rec and rec.get("state") == "unknown":
            return None, ""
        time.sleep(5)
    return None, ""


def rsync_up(remote: Remote, ctx: dict, jobdir: str) -> int:
    src = ctx["sync_dir"].rstrip("/") + "/"
    cmd = ["rsync", "-a", "--delete", "--copy-unsafe-links", "--timeout=120",
           *sync_filters(ctx["sync_dir"], ctx.get("includes", []), ctx.get("excludes", [])),
           "-e", remote.rsync_e(), src, f"{remote.h['ssh']}:{jobdir}/"]
    return subprocess.run(cmd).returncode


def fetch_artifacts(remote: Remote, ctx: dict, jobdir: str) -> None:
    base = ctx["sync_dir"]
    for art in ctx["artifacts"]:
        rel = os.path.normpath(art)
        if rel.startswith("..") or os.path.isabs(rel):
            log(f"artifact {art!r} must be relative to the synced dir; skipped")
            continue
        dest = os.path.join(base, os.path.dirname(rel))
        os.makedirs(dest, exist_ok=True)
        cmd = ["rsync", "-a", "-e", remote.rsync_e(), f"{remote.h['ssh']}:{jobdir}/{rel}", dest + "/"]
        cp = subprocess.run(cmd, capture_output=True, text=True)
        if cp.returncode != 0:
            log(f"artifact {art}: not copied back (rsync exit {cp.returncode})")


# --------------------------------------------------------------------------
# local execution
# --------------------------------------------------------------------------

def run_local_job(ctx: dict, lease: Lease | None, cfg: dict) -> int:
    env = dict(os.environ)
    jobs = cfg["local"]["jobs"].get(ctx["class"], 2)
    env.update({"COMPUTE_JOBS": str(jobs), "COMPUTE_CLASS": ctx["class"], "COMPUTE_HOST": "local",
                "COMPUTE_SLOT": lease.label if lease else "light"})
    env.setdefault("CARGO_BUILD_JOBS", str(jobs))
    pass_fds = tuple(lease.fds) if lease else ()
    try:
        proc = subprocess.Popen(ctx["argv"], cwd=ctx.get("cwd"), env=env, pass_fds=pass_fds, start_new_session=True)
    except FileNotFoundError:
        log(f"command not found: {ctx['argv'][0]}")
        return 127
    except OSError as exc:
        log(f"cannot start: {exc}")
        return 126
    got = {"sig": None}

    def on_signal(signum, _frame):
        if got["sig"] is not None:  # second signal: no more grace
            kill_group(proc, signal.SIGKILL, 0)
            return
        got["sig"] = signum
        kill_group(proc, signum if signum != signal.SIGHUP else signal.SIGTERM, grace=15)

    old = {s: signal.signal(s, on_signal) for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
    try:
        while True:
            try:
                rc = proc.wait()
                break
            except InterruptedError:  # pragma: no cover
                continue
    finally:
        for s, h in old.items():
            signal.signal(s, h)
    if got["sig"] is not None:
        return 128 + got["sig"]
    return 128 - rc if rc < 0 else rc


class Cancelled(Exception):
    def __init__(self, sig):
        self.sig = sig


def cmd_run(args, rest: list[str]) -> int:
    if not rest:
        die("usage: compute run --class heavy|moderate|light [...] -- COMMAND ...", 2)
    cfg = load_config()
    root = state_root(cfg)
    ensure_state(root, cfg)
    cls = args.cls
    host = args.host or cfg["default_host"]
    where = args.where
    sync_dir = os.path.abspath(args.sync) if args.sync else None
    if sync_dir and not os.path.isdir(sync_dir):
        die(f"--sync {args.sync}: not a directory", 2)
    if where not in ("auto", "local"):
        host = where  # an explicit host name; it may run with an empty job dir when no --sync is given
        if host not in cfg["hosts"]:
            die(f"unknown host {host!r}; configured: {', '.join(cfg['hosts']) or 'none (local-only)'}", 2)
    elif where == "auto" and host is None:
        where = "local"  # no remote host configured: local scheduling only
    project = dirname = None
    cwd_rel = "."
    if sync_dir or where not in ("auto", "local"):
        try:
            project, dirname = derive_names(sync_dir or os.getcwd(), args.project, args.name)
        except ValueError as exc:
            die(str(exc), 2)
        if sync_dir:
            cwd = os.path.realpath(os.getcwd())
            rd = os.path.realpath(sync_dir)
            if cwd == rd or cwd.startswith(rd + os.sep):
                cwd_rel = os.path.relpath(cwd, rd)
    ctx = {
        "id": f"{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}", "class": cls, "argv": rest,
        "cmd": " ".join(shlex.quote(a) for a in rest)[:300], "cwd": os.getcwd(), "project": project,
        "dirname": dirname, "sync_dir": sync_dir, "artifacts": args.artifacts or [], "host": host,
        "cwd_rel": cwd_rel, "includes": args.include or [], "excludes": args.exclude or [],
        "ignore_measure": args.ignore_measure,
    }
    proj_label = project or os.path.basename(os.getcwd())

    if cls == "light":
        return run_local_job(ctx, None, cfg)

    pool_name, weight = cfg["local"]["class_pool"][cls]
    pool = Pool(os.path.join(root, "slots"), pool_name, cfg["local"]["pools"][pool_name])
    remote = Remote(cfg, host, root) if where != "local" else None
    info = {"id": ctx["id"], "project": proj_label, "class": cls, "cmd": ctx["cmd"], "pid": os.getpid(),
            "start": time.time(), "host": "local"}
    t0 = time.time()
    poll = float(cfg["poll_seconds"])
    remote_poll = float(cfg["remote_poll_seconds"])

    def local_blocked() -> dict | None:
        return None if args.ignore_measure else measuring(root, "local")

    explicit_remote = where not in ("auto", "local")
    waiter = None
    lease = None
    last_msg = None  # local queue status line
    last_remote_msg = None
    held = {"waiter": None}

    def drop_waiter():  # a job that holds a remote slot must not block the local queue
        if held["waiter"] is not None:
            held["waiter"].close()
            held["waiter"] = None
    ctx["on_ready"] = drop_waiter
    last_remote = 0.0
    unreachable_warned = False
    try:
        if not explicit_remote:
            waiter = held["waiter"] = Waiter(root, cls, {"pid": os.getpid(), "project": proj_label, "cmd": ctx["cmd"],
                                                         "since": time.time(), "class": cls, "id": ctx["id"]})
        while True:
            if not explicit_remote and held["waiter"] is None:  # remote attempt failed after dropping our place
                waiter = held["waiter"] = Waiter(root, cls, {"pid": os.getpid(), "project": proj_label, "cmd": ctx["cmd"],
                                                             "since": time.time(), "class": cls, "id": ctx["id"]})
            # ---- local attempt (head of queue only, FIFO) ----
            if not explicit_remote and held["waiter"] and (args.ignore_measure or held["waiter"].ahead() == 0) and not local_blocked():
                lease = pool.try_acquire(weight, info)
                if lease and local_blocked():  # window opened between check and take
                    lease.release()
                    lease = None
                if lease:
                    break
            # ---- remote attempt ----
            if where != "local" and sync_dir is not None or explicit_remote:
                if time.time() - last_remote >= (remote_poll if last_remote else 0):
                    last_remote = time.time()
                    use_remote = True
                    if not explicit_remote:
                        use_remote = pool_full_or_blocked(pool, weight, local_blocked())
                    if use_remote:
                        status, rc, detail = run_remote(remote, ctx, args)
                        if status == "ran":
                            drop_waiter()
                            if detail and rc not in (0,):
                                log(detail)
                            return rc
                        if status == "unreachable":
                            if not unreachable_warned:
                                log(f"{host} unreachable ({detail}); using the local queue")
                                unreachable_warned = True
                            if explicit_remote and not args.no_fallback:
                                explicit_remote = False
                                waiter = held["waiter"] = Waiter(root, cls, {"pid": os.getpid(), "project": proj_label,
                                                                             "cmd": ctx["cmd"], "since": time.time(), "class": cls})
                            elif explicit_remote:
                                die(f"{host} unreachable ({detail}) and --no-fallback given")
                            where = "local"  # stop retrying a dead host this run
                        elif status == "error":
                            die(detail)
                        elif status == "busy":
                            msg = {"full": f"{host} slots busy", "measuring": f"{host} is in a measurement window",
                                   "dirbusy": f"{host}: another job is using this sync dir"}.get(detail, detail)
                            if msg != last_remote_msg:
                                log(f"queued: {msg}")
                                last_remote_msg = msg
            # ---- status line ----
            if not explicit_remote:
                running = sum(1 for h in pool.holders() if h)
                ahead = held["waiter"].ahead() if held["waiter"] else 0
                blocked = local_blocked()
                msg = ("queued: local measurement window active"
                       if blocked else f"queued behind {running + ahead} jobs ({running} running, {ahead} waiting)")
                if msg != last_msg:
                    log(msg)
                    last_msg = msg
            time.sleep(poll)
    except KeyboardInterrupt:
        drop_waiter()
        log("cancelled while queued")
        return 130
    finally:
        pass

    drop_waiter()
    waited = time.time() - t0
    if waited >= 1:
        log(f"waited {fmt_secs(waited)} for a {cls} slot; running locally ({lease.label})")
    try:
        return run_local_job(ctx, lease, cfg)
    finally:
        lease.release()


def pool_full_or_blocked(pool: Pool, weight: int, blocked) -> bool:
    return bool(blocked) or pool.free_units() < min(weight, pool.units)


# --------------------------------------------------------------------------
# status / measure
# --------------------------------------------------------------------------

def local_status(root: str, cfg: dict) -> dict:
    out: dict = {"pools": {}, "queue": {}, "measuring": measuring(root, "local"), "load": uptime_line()}
    for pname, units in cfg["local"]["pools"].items():
        holders = Pool(os.path.join(root, "slots"), pname, units).holders()
        out["pools"][pname] = {"units": units, "holders": holders}
    for cls in ("heavy", "moderate"):
        out["queue"][cls] = list_waiters(root, cls)
    return out


def describe_holder(h: dict) -> str:
    if h.get("unknown"):
        return "held (details unavailable)"
    age = fmt_secs(time.time() - h.get("start", time.time()))
    return f"{h.get('class', '?')} {h.get('project', '?')} pid={h.get('pid')} {age}: {h.get('cmd', '')[:80]}"


def cmd_status(args) -> int:
    cfg = load_config()
    root = state_root(cfg)
    ensure_state(root, cfg)
    local = local_status(root, cfg)
    hosts: dict = {}
    for name in cfg["hosts"]:
        r = Remote(cfg, name, root)
        hosts[name] = r.probe()
        if hosts[name] is None:
            hosts[name] = {"unreachable": True}
        hosts[name]["local_marker"] = measuring(root, name)
    if args.json:
        print(json.dumps({"local": local, "hosts": hosts}, indent=2))
        return 0
    print("local (this machine)")
    for pname, p in local["pools"].items():
        used = sum(1 for h in p["holders"] if h)
        print(f"  {pname}: {used}/{p['units']} slots used")
        for h in p["holders"]:
            if h:
                print(f"    - {describe_holder(h)}")
    for cls, waiters in local["queue"].items():
        for w in waiters:
            print(f"  queued {cls}: {w.get('project')} pid={w.get('pid')} {fmt_secs(time.time() - w.get('since', time.time()))}: {w.get('cmd', '')[:60]}")
    if local["measuring"]:
        print(f"  MEASURING: {local['measuring']}")
    print(f"  load: {local['load']}")
    for name, st in hosts.items():
        print(f"{name}")
        if st.get("unreachable"):
            print("  unreachable over ssh")
            if st.get("local_marker"):
                print(f"  local marker says MEASURING: {st['local_marker']}")
            continue
        for pname, p in st["pools"].items():
            print(f"  {pname}: {p['units'] - p['free']}/{p['units']} units used ")
        for h in st["running"]:
            print(f"    - {describe_holder(h)}")
        if st.get("measuring"):
            print(f"  MEASURING: {st['measuring']}")
        elif st.get("local_marker"):
            print(f"  local marker present but remote marker missing: {st['local_marker']}")
        print(f"  busy-pattern processes: {len(st.get('ci_workers', []))}")
        print(f"  load: {st.get('load')}")
    return 0


def ci_commands(host_cfg: dict, action: str) -> list[list[str]]:
    """Profile-defined pause/resume commands, run over ssh. `sudo` always gets -n: no password is ever requested."""
    cmds = []
    for cmd in host_cfg.get("pause_commands" if action == "pause" else "resume_commands", []):
        cmd = list(cmd)
        if cmd and cmd[0] == "sudo" and "-n" not in cmd[1:2]:
            cmd.insert(1, "-n")
        cmds.append(cmd)
    return cmds


def sudoers_rule(host_cfg: dict) -> str:
    """A NOPASSWD sudoers rule covering exactly the profile's pause and resume commands."""
    import getpass
    allowed = []
    for action in ("pause", "resume"):
        for cmd in ci_commands(host_cfg, action):
            if cmd[:2] == ["sudo", "-n"]:
                allowed.append(shlex.join(cmd[2:]).replace(",", "\\,"))
    if not allowed:
        return "# no sudo pause/resume commands configured for this host"
    return f"{getpass.getuser()} ALL=(root) NOPASSWD: " + ", \\\n  ".join(allowed)


def print_ci_commands(host_cfg: dict, action: str) -> None:
    for c in ci_commands(host_cfg, action):
        print("    ssh {} {}".format(host_cfg["ssh"], shlex.join(c)))


def cmd_measure(args) -> int:
    cfg = load_config()
    root = state_root(cfg)
    ensure_state(root, cfg)
    host = args.host or cfg["default_host"] or "local"
    os.makedirs(os.path.join(root, "measure"), exist_ok=True)
    is_local = host == "local"
    if not is_local and host not in cfg["hosts"]:
        die(f"unknown host {host!r}", 2)
    hcfg = {} if is_local else cfg["hosts"][host]
    remote = None if is_local else Remote(cfg, host, root)
    info = {"reason": args.reason or "", "owner_pid": os.getppid(), "since": time.time(),
            "since_human": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "by": os.environ.get("USER", "")}

    def running_jobs() -> tuple[list, list, bool]:
        if is_local:
            jobs = [h for p in local_status(root, cfg)["pools"].values() for h in p["holders"] if h]
            return jobs, [], True
        pr = remote.probe()
        if pr is None:
            return [], [], False
        return pr["running"], pr["ci_workers"], True

    if args.action == "sudoers":
        if is_local:
            die("sudoers: pass --host with a configured remote host", 2)
        print(sudoers_rule(hcfg))
        return 0

    if args.action == "status":
        marker = measuring(root, host)
        jobs, workers, reachable = running_jobs()
        print(f"{host}: {'MEASURING ' + json.dumps(marker) if marker else 'no measurement window'}")
        if not is_local:
            pr = remote.probe()
            print(f"  remote marker: {pr['measuring'] if pr else 'unreachable'}")
        print(f"  running broker jobs: {len(jobs)}" + ("" if reachable else " (host unreachable)"))
        for j in jobs:
            print(f"    - {describe_holder(j)}")
        if not is_local:
            print(f"  busy-pattern processes: {len(workers)}")
        return 0

    if args.action == "begin":
        existing = measuring(root, host)
        if existing and not args.force:
            die(f"{host} already has a measurement window: {existing}. Use `compute measure end` or --force.")
        if remote:
            res = remote.ensure_helper() and remote.call(
                "measure", remote.req(action="begin", marker=hcfg["measure_marker"], info=info, force=args.force))
            if not res:
                die(f"cannot reach {host}; no marker written. Retry when ssh works.")
            if not res.get("ok"):
                die(f"remote marker already exists: {res.get('existing')}. Use --force to take over.")
        atomic_write(local_marker_path(root, host), info)
        jobs, workers, _ = running_jobs()
        print(f"measurement window open on {host}: new jobs queue; light jobs and --ignore-measure jobs are unaffected")
        if is_local:
            print("local heavy and moderate jobs now queue until `compute measure end --host local`")
        print(f"running broker jobs to drain: {len(jobs)}")
        for j in jobs:
            print(f"  - {describe_holder(j)}")
        if remote:
            print(f"busy-pattern processes active: {len(workers)}")
            if args.pause and not ci_commands(hcfg, "pause"):
                log("--pause: no pause_commands are configured for this host")
            elif args.pause:
                if workers and not args.force:
                    log("a busy-pattern process is running on the host; not pausing (re-run with --force to override)")
                else:
                    pause_or_resume(remote, hcfg, "pause")
            elif ci_commands(hcfg, "pause"):
                print("pause background services (run these, or use --pause; `compute measure sudoers` prints a sudoers rule):")
                print_ci_commands(hcfg, "pause")
        if args.wait:
            deadline = time.time() + args.wait
            while time.time() < deadline:
                jobs, workers, ok = running_jobs()
                if ok and not jobs and (is_local or not workers):
                    print("host drained")
                    return 0
                time.sleep(5)
            log("timeout: jobs are still running on the host")
            return 3
        return 0 if not jobs else 3

    if args.action == "end":
        if remote:
            res = remote.ensure_helper() and remote.call("measure", remote.req(action="end", marker=hcfg["measure_marker"]))
            if not res:
                log(f"cannot reach {host}; remote marker may remain at {hcfg['measure_marker']}")
        try:
            os.unlink(local_marker_path(root, host))
        except FileNotFoundError:
            pass
        print(f"measurement window closed on {host}")
        if remote:
            if args.resume:
                pause_or_resume(remote, hcfg, "resume")
            elif ci_commands(hcfg, "resume"):
                print("if you paused background services, resume them:")
                print_ci_commands(hcfg, "resume")
        return 0
    return 2


def pause_or_resume(remote: Remote, hcfg: dict, action: str) -> None:
    for cmd in ci_commands(hcfg, action):
        cp = subprocess.run(remote.ssh_argv(shlex.join(cmd)), capture_output=True, text=True)
        label = shlex.join(cmd[2:] if cmd[:2] == ["sudo", "-n"] else cmd)[:80]
        if cp.returncode == 0:
            log(f"{action}: ok {label}")
        else:
            log(f"{action}: FAILED {label}: {cp.stderr.strip().splitlines()[-1] if cp.stderr.strip() else cp.returncode}"
                " (sudo -n needs the NOPASSWD rule; no password is ever sent)")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="compute", description="Two-Mac compute broker")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run a command in a slot: compute run --class heavy -- cargo test")
    r.add_argument("--class", dest="cls", choices=CLASSES, required=True)
    r.add_argument("--where", default="auto", help="auto, local, or a host name from the profile's compute.hosts")
    r.add_argument("--host", help="host used for auto overflow (default from config)")
    r.add_argument("--sync", metavar="DIR", help="portable job: rsync DIR to the remote host when it runs there")
    r.add_argument("--artifacts", nargs="+", metavar="PATH", help="paths relative to --sync DIR to copy back")
    r.add_argument("--project", help="override the remote project name")
    r.add_argument("--name", help="override the remote dir name")
    r.add_argument("--include", action="append", help="extra rsync include pattern")
    r.add_argument("--exclude", action="append", help="extra rsync exclude pattern")
    r.add_argument("--ignore-measure", action="store_true", help="run even inside a measurement window")
    r.add_argument("--no-fallback", action="store_true", help="fail instead of falling back when the host is unreachable")
    s = sub.add_parser("status", help="slots, queue, measurement windows and load on both Macs")
    s.add_argument("--json", action="store_true")
    m = sub.add_parser("measure", help="exclusive measurement window on a host")
    m.add_argument("action", choices=["begin", "end", "status", "sudoers"])
    m.add_argument("--host", help="a configured host name (default: compute.default_host), or local")
    m.add_argument("--reason")
    m.add_argument("--wait", type=int, metavar="SECONDS", help="begin: wait for running jobs to drain")
    m.add_argument("--force", action="store_true")
    m.add_argument("--pause", action="store_true", help="begin: run the host's configured pause commands (sudo -n only)")
    m.add_argument("--resume", action="store_true", help="end: run the host's configured resume commands (sudo -n only)")
    return ap


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "_remote":
        return cmd_remote(argv[1:])
    rest: list[str] = []
    if "--" in argv:
        i = argv.index("--")
        argv, rest = argv[:i], argv[i + 1:]
    args = build_parser().parse_args(argv)
    if args.cmd == "run":
        return cmd_run(args, rest)
    if args.cmd == "status":
        return cmd_status(args)
    return cmd_measure(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
