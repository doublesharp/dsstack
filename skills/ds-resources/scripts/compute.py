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
import platform
import re
import select
import shlex
import signal
import socket
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


def normalize_arch(value: str | None) -> str | None:
    if not value:
        return None
    v = value.lower()
    return {"aarch64": "arm64", "arm64": "arm64", "x86_64": "x86_64", "amd64": "x86_64", "x64": "x86_64"}.get(v, v)


def this_arch() -> str:
    return normalize_arch(platform.machine()) or "unknown"


def default_balance() -> dict:
    return {
        # Estimated finish time is multiplied by these on the local machine, so ties go local.
        "local_bias": {"interactive": 0.8, "batch": 0.9},
        # Seconds of work on an idle speed-1.0 machine, used when --expect is not given.
        "work_seconds": {"light": 5, "moderate": 60, "heavy": 600},
        "sync_default_seconds": 10,       # first-time rsync estimate; later runs use the last measured time
        "cache_seconds": 5,               # how long a remote load sample is reused, across processes
        "recent_seconds": 90,             # recently started jobs' threads count against load until it catches up
        "batch_remote_ratio": 6,          # batch work keeps off a host's interactive reserve unless the other host is this much slower
        "down_seconds": 30,               # skip an unreachable host for this long
    }


def default_machine(entry: dict, local: bool = False) -> dict:
    """Capacity of one machine. Units are a pool; a heavy job takes 2, moderate 1, so the default is one heavy or two moderate."""
    cpus = os.cpu_count() or 4
    base = {
        "slots": {"shared": 2 * max(1, cpus // 4)} if local else {"shared": 2},
        "classes": {"heavy": ["shared", 2], "moderate": ["shared", 1]},
        "jobs": ({"heavy": max(2, cpus - 2), "moderate": max(2, cpus // 3), "light": 2} if local
                 else {"heavy": 8, "moderate": 4, "light": 2}),
        "speed": 1.0,           # relative per-logical-CPU speed; a number, or "auto" to use `compute calibrate`
        "arch": None,           # arm64 | x86_64; local defaults to this machine, remotes to what the host reports
        "max_norm_load": None,  # optional: skip the machine above this load average / CPUs
        "interactive_reserve": 0,  # units batch jobs leave free for latency-sensitive ones
    }
    base.update(entry)
    return base


def default_config() -> dict:
    return {
        "state": None,
        "default_host": None,
        "hosts": {},
        "local": default_machine({}, local=True),
        "balance": default_balance(),
        "poll_seconds": 0.5,
        "remote_poll_seconds": 5,
    }


def default_host(entry: dict) -> dict:
    base = default_machine({}, local=False)
    base.update({
        "ssh": None, "python": "python3", "root": "~/compute", "env_dir": None,
        "measure_marker": "~/compute/MEASURING", "path_prepend": ["~/.cargo/bin"],
        "busy_pattern": "Runner.Worker", "pause_commands": [], "resume_commands": [],
    })
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


def check_machine(where: str, m: dict, path: str) -> None:
    """Reject the pre-balancing profile format and malformed capacity settings with a message that says what to change."""
    slots, classes = m["slots"], m["classes"]
    if not isinstance(slots, dict) or not all(isinstance(v, int) and v > 0 for v in slots.values()):
        die(f"profile {path}: {where}.slots must map pool names to positive integers")
    if set(slots) & {"heavy", "moderate"} and any(isinstance(sp, list) and sp and sp[0] not in slots for sp in classes.values()):
        die(f"profile {path}: {where}.slots uses the old separate heavy/moderate pools; use "
            f'slots {{"shared": N}} with classes {{"heavy": ["shared", 2], "moderate": ["shared", 1]}} (units, not jobs)')
    for cls, spec in classes.items():
        if cls not in CLASSES or not (isinstance(spec, list) and len(spec) == 2 and spec[0] in slots and isinstance(spec[1], int)):
            die(f"profile {path}: {where}.classes[{cls!r}] must be [pool, units] naming a pool in {where}.slots")
    sp = m["speed"]
    if sp != "auto" and (isinstance(sp, bool) or not isinstance(sp, (int, float)) or sp <= 0):
        die(f"profile {path}: {where}.speed must be a positive number or \"auto\"")
    m["arch"] = normalize_arch(m["arch"])
    if m["max_norm_load"] is not None and not (isinstance(m["max_norm_load"], (int, float)) and m["max_norm_load"] > 0):
        die(f"profile {path}: {where}.max_norm_load must be a positive number")
    m["pools"], m["class_pool"] = slots, classes


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
    allowed = {"state", "default_host", "hosts", "local", "balance", "poll_seconds", "remote_poll_seconds"}
    if user.keys() - allowed:
        die(f"profile {path}: unknown compute fields {sorted(user.keys() - allowed)}")
    for key in ("state", "default_host", "poll_seconds", "remote_poll_seconds"):
        if key in user:
            cfg[key] = user[key]
    if "local" in user:
        cfg["local"] = default_machine(user["local"], local=True)
        cfg["local"]["jobs"] = {**default_machine({}, local=True)["jobs"], **user["local"].get("jobs", {})}
    for key, val in user.get("balance", {}).items():
        if key not in cfg["balance"]:
            die(f"profile {path}: unknown balance field {key!r}")
        cfg["balance"][key] = {**cfg["balance"][key], **val} if isinstance(val, dict) else val
    for name, entry in user.get("hosts", {}).items():
        safe_name(name, "host")
        cfg["hosts"][name] = default_host(dict(entry, name=name))
        cfg["hosts"][name]["jobs"] = {**default_host({})["jobs"], **entry.get("jobs", {})}
    if cfg["default_host"] is None and len(cfg["hosts"]) == 1:
        cfg["default_host"] = next(iter(cfg["hosts"]))
    if cfg["default_host"] is not None and cfg["default_host"] not in cfg["hosts"]:
        die(f"profile {path}: default_host {cfg['default_host']!r} is not in compute.hosts")
    check_machine("local", cfg["local"], path)
    cfg["local"]["arch"] = cfg["local"]["arch"] or this_arch()
    for hname, h in cfg["hosts"].items():
        check_machine(f"hosts.{hname}", h, path)
        h["env_dir"] = h["env_dir"] or h["root"].rstrip("/") + "/env"
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
    def __init__(self, root: str, pool: str, info: dict):
        self.dir = os.path.join(root, "queue", pool)
        os.makedirs(self.dir, exist_ok=True)
        self.path = os.path.join(self.dir, f"{time.time_ns():020d}-{os.getpid()}.json")
        self.fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o644)
        fcntl.flock(self.fd, fcntl.LOCK_EX)
        self.info = dict(info)
        atomic_write_fd(self.fd, json.dumps(info))

    def update(self, **fields) -> None:
        if any(self.info.get(k) != v for k, v in fields.items()):
            self.info.update(fields)
            atomic_write_fd(self.fd, json.dumps(self.info))

    def ahead(self) -> int:
        """Earlier live waiters that are really contending for local units (not pinned elsewhere or held back)."""
        n = 0
        for name in sorted(os.listdir(self.dir)):
            full = os.path.join(self.dir, name)
            if full == self.path:
                return n
            if waiter_alive(full) and (read_json(full) or {}).get("contending", True):
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


def list_waiters(root: str, pool: str) -> list[dict]:
    d = os.path.join(root, "queue", pool)
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


DEFAULT_WINDOW_SECONDS = 3 * 3600
ONE_SHOT_SHELLS = {"sh", "bash", "zsh", "dash", "fish", "ksh"}


def parse_duration(text: str) -> float:
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([smh])", text.strip())
    if not m:
        raise ValueError(f"duration {text!r} needs a unit: 90s, 45m or 3h")
    return float(m.group(1)) * {"s": 1, "m": 60, "h": 3600}[m.group(2)]


def proc_start(pid) -> str | None:
    """Start time of a process, to tell it from a later process that reused the pid."""
    try:
        out = subprocess.run(["ps", "-o", "lstart=", "-p", str(int(pid))], capture_output=True, text=True, timeout=5)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() or None


def proc_name(pid) -> str:
    try:
        out = subprocess.run(["ps", "-o", "comm=", "-p", str(int(pid))], capture_output=True, text=True, timeout=5)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return ""
    return os.path.basename(out.stdout.strip()).lstrip("-")


def window_info(reason: str, max_seconds: float, owner_pid) -> dict:
    now = time.time()
    return {"reason": reason, "since": now, "since_human": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(now)),
            "by": os.environ.get("USER", ""), "owner_host": socket.gethostname(), "owner_pid": owner_pid,
            "owner_start": proc_start(owner_pid) if owner_pid else None, "max_seconds": max_seconds,
            "expires": now + max_seconds}


def window_status(marker: dict, now: float | None = None, check_owner: bool = True) -> dict:
    """Is a measurement window still in force? The owner's pid is checked only on the host it was recorded on;
    elsewhere, or when no owner was recorded, only the maximum duration applies."""
    now = now or time.time()
    expires = marker.get("expires") or (marker.get("since", now) + DEFAULT_WINDOW_SECONDS)
    pid, owner = marker.get("owner_pid"), "untracked"
    if pid and marker.get("owner_host") == socket.gethostname() and check_owner:
        start = marker.get("owner_start")
        owner = "alive" if pid_alive(pid) and (not start or proc_start(pid) == start) else "exited"
    elif pid:
        owner = "unknown (owner is on another host)"
    status = {"owner": owner, "remaining": expires - now, "ended": None}
    if owner == "exited":
        status["ended"] = f"owner pid {pid} exited"
    elif now > expires:
        status["ended"] = f"past its {fmt_secs(marker.get('max_seconds') or DEFAULT_WINDOW_SECONDS)} maximum"
    return status


def describe_window(marker: dict) -> str:
    st = window_status(marker)
    owner = f"pid {marker.get('owner_pid')} on {marker.get('owner_host')}: {st['owner']}" if marker.get("owner_pid") else "no owner tracked"
    return (f"\"{marker.get('reason', '')}\" since {marker.get('since_human', '?')}, owner {owner}, "
            f"{'ends in ' + fmt_secs(st['remaining']) if st['remaining'] > 0 else 'past its maximum'}")


def measuring(root: str, host: str) -> dict | None:
    """The host's window marker, or None. A window whose owner is gone or that outlived its maximum is cleared here."""
    marker = read_json(local_marker_path(root, host))
    if not marker:
        return None
    st = window_status(marker)
    if st["ended"]:
        log(f"measurement window on {host} ended ({st['ended']}); markers cleared")
        try:
            os.unlink(local_marker_path(root, host))
        except OSError:
            pass
        forget_sample(root, host)
        return None
    return marker


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


def machine_facts() -> dict:
    try:
        load = os.getloadavg()
    except OSError:
        load = (0.0, 0.0, 0.0)
    return {"load1": load[0], "load5": load[1], "cpus": os.cpu_count() or 1, "arch": this_arch()}


def bench(seconds: float = 1.0) -> float:
    """Single-thread integer/dict/float mix per CPU-second (process time, so a busy host is not penalised for waiting)."""
    import math
    start = time.process_time()
    done, x, acc, table = 0, 1, 0.0, {}
    while time.process_time() - start < seconds:
        for i in range(20000):
            x = (x * 1103515245 + 12345) & 0x7FFFFFFF
            table[x & 1023] = table.get(x & 1023, 0) + (x % 7)
            acc += math.sqrt(i + 1)
        done += 20000
    return done / max(time.process_time() - start, 1e-6)


def remote_bench(req: dict) -> dict:
    return {"score": bench(float(req.get("seconds", 1.0))), **machine_facts()}


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
    out.update(machine_facts())
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
                    "cmd": req.get("cmd", ""), "pid": os.getpid(), "start": time.time(), "host": "remote",
                    "threads": int(req.get("jobs", 1))}
            lease = pool.try_acquire(int(req["weight"]), info, inheritable=False)
            if lease is None:
                say("BUSY", {"reason": "full", "running": [h for h in pool.holders() if h]})
                return EXIT_BUSY
            marker = req.get("marker")
            mk = read_json(_expand(marker)) if marker else None
            if mk and window_status(mk, check_owner=False)["ended"]:
                mk = None  # past its maximum; the client clears the file
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
    handlers = {"probe": remote_probe, "bench": remote_bench, "measure": remote_measure, "result": remote_result, "kill": remote_kill}
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
            started = time.time()
            rc = rsync_up(remote, ctx, jobdir)
            if rc in (0, 23, 24) and ctx.get("state_root"):
                record_sync(ctx["state_root"], sync_key(ctx["host"], ctx.get("project"), ctx.get("dirname")),
                            time.time() - started)
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


# --------------------------------------------------------------------------
# placement: load snapshots and the ranking function
# --------------------------------------------------------------------------

def unique_jobs(holders) -> list[dict]:
    seen, out = set(), []
    for h in holders:
        if h and (h.get("id") or id(h)) not in seen:
            seen.add(h.get("id") or id(h))
            out.append(h)
    return out


def scan_slots(root: str, cfg: dict) -> dict:
    """Holders of every lock file under slots/, including pools the profile no longer defines (older heavy/moderate locks)."""
    d = os.path.join(root, "slots")
    found: dict[str, int] = {}
    if os.path.isdir(d):
        for name in os.listdir(d):
            m = re.match(r"^(.+)\.(\d+)\.lock$", name)
            if m:
                found[m.group(1)] = max(found.get(m.group(1), 0), int(m.group(2)) + 1)
    for pname, units in cfg["local"]["slots"].items():
        found[pname] = max(found.get(pname, 0), units)
    return {pname: {"units": units, "holders": Pool(d, pname, units).holders()} for pname, units in sorted(found.items())}


def legacy_units(pools: dict, cfg: dict) -> int:
    """Units held through pools the profile no longer defines, charged by class so they still count against capacity."""
    used = 0
    for pname, p in pools.items():
        if pname in cfg["local"]["slots"]:
            continue
        for job in unique_jobs(p["holders"]):
            used += cfg["local"]["classes"].get(job.get("class", ""), ["", 1])[1]
    return used


def recent_threads(jobs: list[dict], bal: dict, now: float) -> float:
    """Threads of jobs started a moment ago: the load average has not seen them yet."""
    window = float(bal["recent_seconds"])
    return sum(float(j.get("threads", 0)) * max(0.0, 1 - (now - j.get("start", 0)) / window) for j in jobs)


def calibration(root: str) -> dict:
    return read_json(os.path.join(root, "calibration.json")) or {}


def resolve_speed(machine: dict, name: str, calib: dict) -> tuple[float, str]:
    if machine["speed"] != "auto":
        return float(machine["speed"]), "profile"
    base, mine = calib.get("local", {}).get("score"), calib.get(name, {}).get("score")
    if base and mine:
        return round(mine / base, 3), "calibrated"
    return 1.0, "default (run `compute calibrate`)"


def fake_facts(name: str) -> dict:
    """Test hook: COMPUTE_FAKE_LOADS='{"local": {"load1": 15, "cpus": 12}}' overrides sampled load, cpus or arch."""
    raw = os.environ.get("COMPUTE_FAKE_LOADS")
    return json.loads(raw).get(name, {}) if raw else {}


def build_snapshot(name: str, machine: dict, facts: dict, pools: dict, running: list, measuring_marker, cfg: dict,
                   calib: dict, down: bool = False) -> dict:
    facts = {**facts, **fake_facts(name)}
    speed, source = resolve_speed(machine, name, calib)
    cpus = int(facts.get("cpus") or 1)
    load1 = float(facts.get("load1") or 0.0)
    recent = recent_threads(running, cfg["balance"], time.time())
    eff_load = load1 + recent
    return {
        "name": name, "local": name == "local", "down": down, "cpus": cpus, "load1": load1, "recent_threads": round(recent, 2),
        "norm_load": round(eff_load / cpus, 3), "arch": machine.get("arch") or normalize_arch(facts.get("arch")),
        "speed": speed, "speed_source": source, "pools": pools, "running": running, "measuring": measuring_marker,
        "max_norm_load": machine.get("max_norm_load"), "reserve": machine.get("interactive_reserve", 0),
        "jobs": machine["jobs"], "classes": machine["classes"],
        "free_cpu_capacity": round(max(0.0, cpus - eff_load) * speed, 2),
        "window": window_status(measuring_marker) if measuring_marker else None,
    }


def local_snapshot(root: str, cfg: dict) -> dict:
    pools = scan_slots(root, cfg)
    running = unique_jobs(h for p in pools.values() for h in p["holders"])
    view = {}
    for pname, p in pools.items():
        if pname in cfg["local"]["slots"]:
            used = sum(1 for h in p["holders"] if h)
            view[pname] = {"units": p["units"], "free": max(0, p["units"] - used - legacy_units(pools, cfg))}
    return build_snapshot("local", cfg["local"], machine_facts(), view, running, measuring(root, "local"), cfg,
                          calibration(root))


def remote_snapshot(cfg: dict, name: str, root: str, remotes: dict, force: bool = False) -> dict:
    """Probe a remote host, reusing a sample younger than balance.cache_seconds (shared by every process)."""
    bal = cfg["balance"]
    os.makedirs(os.path.join(root, "load"), exist_ok=True)
    cache_path = os.path.join(root, "load", f"{name}.json")
    cached = read_json(cache_path) or {}
    now = time.time()
    data = None
    if not force and cached.get("down_until", 0) > now:
        pass
    elif not force and cached.get("data") and now - cached.get("ts", 0) < float(bal["cache_seconds"]):
        data = cached["data"]
    else:
        remote = remotes.setdefault(name, Remote(cfg, name, root))
        data = remote.probe()
        if data is None:
            atomic_write(cache_path, {"ts": now, "data": None, "down_until": now + float(bal["down_seconds"])})
        else:
            atomic_write(cache_path, {"ts": now, "data": data})
    machine = cfg["hosts"][name]
    if data is None:
        return build_snapshot(name, machine, {}, {}, [], measuring(root, name), cfg, calibration(root), down=True)
    marker = data.get("measuring")
    if marker:
        ended = window_status(marker)["ended"]
        if ended:
            log(f"measurement window on {name} ended ({ended}); clearing its markers")
            remote = remotes.setdefault(name, Remote(cfg, name, root))
            remote.call("measure", remote.req(action="end", marker=machine["measure_marker"]))
            try:
                os.unlink(local_marker_path(root, name))
            except OSError:
                pass
            forget_sample(root, name)
            marker = None
    return build_snapshot(name, machine, data, data.get("pools", {}), data.get("running", []),
                          marker or measuring(root, name), cfg, calibration(root))


def forget_sample(root: str, name: str) -> None:
    try:
        os.unlink(os.path.join(root, "load", f"{name}.json"))
    except OSError:
        pass


def sync_key(host: str, project: str | None, dirname: str | None) -> str:
    return f"{host}|{project}|{dirname}"


def record_sync(root: str, key: str, seconds: float) -> None:
    path = os.path.join(root, "sync-times.json")
    data = read_json(path) or {}
    data[key] = round(seconds, 2)
    atomic_write(path, data)


def rank_hosts(job: dict, snaps: list[dict], bal: dict) -> dict:
    """Pure placement decision.

    job: class, latency (interactive|batch), arch (any|arm64|x86_64), work (seconds on an idle speed-1.0 host),
         ignore_measure, sync (host -> estimated rsync seconds).
    Estimated finish = sync + work * max(1, (load + recent starts + job threads) / cpus) / speed. The local machine's
    estimate is scaled by balance.local_bias, so near-ties stay local. Batch jobs keep off a machine's
    interactive_reserve while another candidate exists, unless that candidate is balance.batch_remote_ratio times slower.
    """
    cls, latency = job["class"], job["latency"]
    options = []
    for sn in snaps:
        pool, weight = sn["classes"].get(cls, [None, 0]) if cls != "light" else (None, 0)
        free = sn["pools"].get(pool, {}).get("free", 0) if pool else 0
        threads = sn["jobs"].get(cls, 1)
        slowdown = max(1.0, (sn["load1"] + sn["recent_threads"] + threads) / sn["cpus"]) / sn["speed"]
        finish = job["work"] * slowdown + (0 if sn["local"] else job["sync"].get(sn["name"], bal["sync_default_seconds"]))
        if sn["local"]:
            finish *= bal["local_bias"][latency]
        why = None
        if job["arch"] != "any" and sn["arch"] != job["arch"]:
            why = "arch"
        elif sn["down"]:
            why = "down"
        elif sn["measuring"] and not job.get("ignore_measure"):
            why = "measuring"
        elif sn["max_norm_load"] and sn["norm_load"] > sn["max_norm_load"]:
            why = "load"
        elif weight and free < weight:
            why = "full"
        held = bool(why in (None, "full") and weight and latency == "batch" and sn["reserve"]
                    and free - weight < sn["reserve"])
        options.append({"host": sn["name"], "finish": round(finish, 1), "slowdown": round(slowdown, 3), "why": why,
                        "held_back": held, "free": free, "weight": weight, "load1": sn["load1"], "cpus": sn["cpus"],
                        "speed": sn["speed"], "norm_load": sn["norm_load"], "threads": threads})
    alternatives = [o for o in options if o["why"] in (None, "full") and not o["held_back"]]
    for o in options:
        if o["held_back"] and alternatives:
            best = min(x["finish"] for x in alternatives)
            if not best > bal["batch_remote_ratio"] * o["finish"]:
                o["why"] = "reserved"
    order = sorted((o for o in options if o["why"] is None), key=lambda o: o["finish"])
    contending = any(o["host"] == "local" and o["why"] in (None, "full") for o in options)
    return {"order": order, "options": options, "local_contending": contending}


def explain(job: dict, ranking: dict, chosen: str) -> str:
    parts = []
    for o in sorted(ranking["options"], key=lambda o: o["finish"]):
        note = "" if o["why"] is None else f" [{o['why']}]"
        parts.append(f"{o['host']} ~{o['finish']:g}s (load {o['load1']:.1f}/{o['cpus']}, speed {o['speed']:g}, "
                     f"{o['free']} free units){note}")
    return f"{job['class']}/{job['latency']} -> {chosen}: " + "; ".join(parts)


def record_decision(root: str, entry: dict) -> None:
    path = os.path.join(root, "placements.jsonl")
    try:
        with open(path, "a") as fh:
            fh.write(json.dumps(entry) + "\n")
        if os.path.getsize(path) > 64 * 1024:
            with open(path) as fh:
                keep = fh.readlines()[-100:]
            atomic_write(path, "".join(keep))
    except OSError:
        pass


def recent_decisions(root: str, n: int = 5) -> list[dict]:
    try:
        with open(os.path.join(root, "placements.jsonl")) as fh:
            lines = fh.readlines()[-n:]
        return [json.loads(x) for x in lines]
    except (OSError, ValueError):
        return []


def wait_message(job: dict, ranking: dict, running: int, ahead: int) -> str:
    notes = []
    for o in ranking["options"]:
        if o["why"] == "full" and o["host"] == "local":
            notes.append(f"queued behind {running + ahead} jobs ({running} running, {ahead} waiting)")
        elif o["why"] == "full":
            notes.append(f"{o['host']} slots busy")
        elif o["why"] == "measuring":
            notes.append("local measurement window active" if o["host"] == "local"
                         else f"{o['host']} is in a measurement window")
        elif o["why"] == "down":
            notes.append(f"{o['host']} unreachable")
        elif o["why"] == "load":
            notes.append(f"{o['host']} load too high")
        elif o["why"] == "reserved":
            notes.append(f"{o['host']} keeps its interactive reserve free")
    return "queued: " + "; ".join(notes) if notes else "queued"


def cmd_run(args, rest: list[str]) -> int:
    if not rest:
        die("usage: compute run --class heavy|moderate|light [...] -- COMMAND ...", 2)
    cfg = load_config()
    root = state_root(cfg)
    ensure_state(root, cfg)
    bal = cfg["balance"]
    cls = args.cls
    where = args.where
    sync_dir = os.path.abspath(args.sync) if args.sync else None
    if sync_dir and not os.path.isdir(sync_dir):
        die(f"--sync {args.sync}: not a directory", 2)
    arch = "any" if args.arch == "any" else normalize_arch(args.arch)
    explicit_host = where if where not in ("auto", "local") else None
    if explicit_host and explicit_host not in cfg["hosts"]:
        die(f"unknown host {explicit_host!r}; configured: {', '.join(cfg['hosts']) or 'none (local-only)'}", 2)
    if explicit_host:
        allowed = [explicit_host]
    elif where == "local":
        allowed = ["local"]
    else:
        allowed = ["local"] + (list(cfg["hosts"]) if sync_dir else [])
    local_ok = arch == "any" or cfg["local"]["arch"] == arch
    if arch != "any":
        allowed = [h for h in allowed if (cfg["local"]["arch"] if h == "local" else cfg["hosts"][h]["arch"]) in (arch, None)]
        if not allowed:
            hint = "" if sync_dir or explicit_host else " (add --sync DIR so the job can run on another host)"
            die(f"no eligible host has --arch {arch}{hint}", 2)
    project = dirname = None
    cwd_rel = "."
    remote_allowed = [h for h in allowed if h != "local"]
    if remote_allowed:
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
        "dirname": dirname, "sync_dir": sync_dir, "artifacts": args.artifacts or [], "host": None,
        "cwd_rel": cwd_rel, "includes": args.include or [], "excludes": args.exclude or [],
        "ignore_measure": args.ignore_measure, "state_root": root,
    }
    proj_label = project or os.path.basename(os.getcwd())
    if cls == "light" and "local" in allowed and local_ok:
        return run_local_job(ctx, None, cfg)

    latency = args.latency or ("batch" if cls == "heavy" else "interactive")
    sync_times = read_json(os.path.join(root, "sync-times.json")) or {}
    job = {"class": cls, "latency": latency, "arch": arch, "ignore_measure": args.ignore_measure,
           "work": float(args.expect or bal["work_seconds"][cls]),
           "sync": {h: sync_times.get(sync_key(h, project, dirname), bal["sync_default_seconds"]) for h in remote_allowed}}
    pool_name, weight = cfg["local"]["classes"].get(cls, [None, 0]) if cls != "light" else (None, 0)
    pool = Pool(os.path.join(root, "slots"), pool_name, cfg["local"]["slots"][pool_name]) if pool_name else None
    remotes: dict = {}
    t0 = time.time()
    poll = float(cfg["poll_seconds"])
    info = {"id": ctx["id"], "project": proj_label, "class": cls, "cmd": ctx["cmd"], "pid": os.getpid(),
            "start": time.time(), "host": "local", "threads": cfg["local"]["jobs"].get(cls, 1)}
    held = {"waiter": None}

    def drop_waiter():  # a job that holds a remote slot must not block the local queue
        if held["waiter"] is not None:
            held["waiter"].close()
            held["waiter"] = None
    ctx["on_ready"] = drop_waiter
    busy_until: dict[str, float] = {}
    last_msg = None
    unreachable_warned = set()
    lease = None
    try:
        while True:
            if "local" in allowed and pool and held["waiter"] is None:
                held["waiter"] = Waiter(root, pool_name, {"pid": os.getpid(), "project": proj_label, "cmd": ctx["cmd"],
                                                          "since": time.time(), "class": cls, "weight": weight,
                                                          "contending": True})
            snaps = []
            for h in allowed:
                if h == "local":
                    snaps.append(local_snapshot(root, cfg))
                else:
                    sn = remote_snapshot(cfg, h, root, remotes)
                    if busy_until.get(h, 0) > time.time() and sn["pools"].get(cfg["hosts"][h]["classes"].get(cls, [""])[0]):
                        sn["pools"] = {k: dict(v, free=0) for k, v in sn["pools"].items()}
                    snaps.append(sn)
            ranking = rank_hosts(job, snaps, bal)
            if arch != "any" and all(o["why"] == "arch" for o in ranking["options"]):
                die(f"no eligible host has --arch {arch}", 2)
            if explicit_host and any(o["host"] == explicit_host and o["why"] == "down" for o in ranking["options"]):
                if args.no_fallback or not local_ok:
                    die(f"{explicit_host} unreachable and no fallback is allowed")
                if explicit_host not in unreachable_warned:
                    log(f"{explicit_host} unreachable; using the local queue")
                    unreachable_warned.add(explicit_host)
                allowed = ["local"]
                continue
            if held["waiter"] is not None:
                held["waiter"].update(contending=ranking["local_contending"])
            for opt in ranking["order"]:
                if opt["host"] == "local":
                    w = held["waiter"]
                    if pool is None or w is None or args.ignore_measure or w.ahead() == 0:
                        lease = pool.try_acquire(weight, info) if pool else None
                        if lease and not args.ignore_measure and measuring(root, "local"):
                            lease.release()  # a window opened between the check and the take
                            lease = None
                        if lease or pool is None:
                            chosen = "local"
                            break
                    continue
                ctx["host"] = opt["host"]
                remote = remotes.setdefault(opt["host"], Remote(cfg, opt["host"], root))
                status, rc, detail = run_remote(remote, ctx, args)
                if status == "ran":
                    drop_waiter()
                    record_decision(root, {"ts": time.time(), "project": proj_label, "class": cls, "latency": latency,
                                           "chosen": opt["host"], "why": explain(job, ranking, opt["host"])})
                    if detail and rc != 0:
                        log(detail)
                    return rc
                if status == "unreachable":
                    atomic_write(os.path.join(root, "load", f"{opt['host']}.json"),
                                 {"ts": time.time(), "data": None, "down_until": time.time() + float(bal["down_seconds"])})
                    if opt["host"] not in unreachable_warned:
                        log(f"{opt['host']} unreachable ({detail}); considering other hosts")
                        unreachable_warned.add(opt["host"])
                elif status == "error":
                    die(detail)
                else:  # busy: someone else took the slot after the sample was taken
                    busy_until[opt["host"]] = time.time() + float(cfg["remote_poll_seconds"])
            else:
                running = sum(1 for h in snaps[0]["running"]) if snaps and snaps[0]["local"] else 0
                ahead = held["waiter"].ahead() if held["waiter"] else 0
                msg = wait_message(job, ranking, running, ahead)
                if msg != last_msg:
                    log(msg)
                    last_msg = msg
                time.sleep(poll)
                continue
            break
    except KeyboardInterrupt:
        drop_waiter()
        log("cancelled while queued")
        return 130

    drop_waiter()
    if len(ranking["options"]) > 1:
        log("placement: " + explain(job, ranking, chosen))
    record_decision(root, {"ts": time.time(), "project": proj_label, "class": cls, "latency": latency,
                           "chosen": "local", "why": explain(job, ranking, "local")})
    waited = time.time() - t0
    if waited >= 1 and lease:
        log(f"waited {fmt_secs(waited)} for a {cls} slot; running locally ({lease.label})")
    try:
        return run_local_job(ctx, lease, cfg)
    finally:
        if lease:
            lease.release()


# --------------------------------------------------------------------------
# status / balance / calibrate / measure
# --------------------------------------------------------------------------

def local_status(root: str, cfg: dict) -> dict:
    out: dict = {"pools": {}, "queue": {}, "measuring": measuring(root, "local"), "load": uptime_line()}
    for pname, p in scan_slots(root, cfg).items():
        out["pools"][pname] = p
    for pname in cfg["local"]["slots"]:
        out["queue"][pname] = list_waiters(root, pname)
    return out


def describe_holder(h: dict) -> str:
    if h.get("unknown"):
        return "held (details unavailable)"
    age = fmt_secs(time.time() - h.get("start", time.time()))
    return f"{h.get('class', '?')} {h.get('project', '?')} pid={h.get('pid')} {age}: {h.get('cmd', '')[:80]}"


def gather(cfg: dict, root: str) -> dict:
    local = local_status(root, cfg)
    snaps = {"local": local_snapshot(root, cfg)}
    remotes: dict = {}
    for name in cfg["hosts"]:
        snaps[name] = remote_snapshot(cfg, name, root, remotes, force=True)
    return {"local": local, "snapshots": snaps}


def plans(cfg: dict, snaps: dict, arch: str = "any") -> list[dict]:
    bal = cfg["balance"]
    out = []
    for cls, latency in (("heavy", "batch"), ("moderate", "interactive"), ("heavy", "interactive")):
        job = {"class": cls, "latency": latency, "arch": arch, "work": bal["work_seconds"][cls], "sync": {}}
        ranking = rank_hosts(job, list(snaps.values()), bal)
        chosen = ranking["order"][0]["host"] if ranking["order"] else None
        out.append({"class": cls, "latency": latency, "chosen": chosen, "explain": explain(job, ranking, chosen or "(queue)")})
    return out


def print_host(name: str, sn: dict, root: str) -> None:
    if sn["down"]:
        print(f"{name}: unreachable over ssh")
        return
    pools = ", ".join(f"{pn} {p['units'] - p['free']}/{p['units']} units used" for pn, p in sn["pools"].items())
    print(f"{name}: load {sn['load1']:.1f} on {sn['cpus']} cpus (normalized {sn['norm_load']:.2f}"
          f"{', incl. ' + format(sn['recent_threads'], 'g') + ' recent threads' if sn['recent_threads'] else ''}), "
          f"speed {sn['speed']:g} [{sn['speed_source']}], arch {sn['arch']}")
    print(f"  effective free capacity {sn['free_cpu_capacity']:g} (free cpus x speed); {pools}")
    if sn["measuring"]:
        print(f"  MEASURING: {describe_window(sn['measuring'])}")
    for j in sn["running"]:
        print(f"    - {describe_holder(j)} [{j.get('threads', '?')} threads]")


def cmd_status(args) -> int:
    cfg = load_config()
    root = state_root(cfg)
    ensure_state(root, cfg)
    g = gather(cfg, root)
    local, snaps = g["local"], g["snapshots"]
    decisions = recent_decisions(root)
    if args.json:
        hosts = {}
        for name in cfg["hosts"]:
            sn = snaps[name]
            hosts[name] = {"unreachable": True} if sn["down"] else {
                **sn, "running": sn["running"], "pools": sn["pools"]}
            hosts[name]["local_marker"] = measuring(root, name)
        print(json.dumps({"local": {**local, **{k: v for k, v in snaps["local"].items() if k not in ("pools", "running")}},
                          "hosts": hosts, "decisions": decisions, "plan": plans(cfg, snaps)}, indent=2))
        return 0
    print_host("local (this machine)", snaps["local"], root)
    for pname, p in local["pools"].items():
        legacy = "" if pname in cfg["local"]["slots"] else "  (older pool, still held)"
        for h in unique_jobs(p["holders"]):
            if not legacy:
                continue
            print(f"    - {describe_holder(h)}{legacy}")
    for pname, waiters in local["queue"].items():
        for w in waiters:
            print(f"  queued {w.get('class')}: {w.get('project')} pid={w.get('pid')} "
                  f"{fmt_secs(time.time() - w.get('since', time.time()))}: {w.get('cmd', '')[:60]}")
    for name in cfg["hosts"]:
        print_host(name, snaps[name], root)
        if snaps[name]["down"] and measuring(root, name):
            print(f"  local marker says MEASURING: {measuring(root, name)}")
    if decisions:
        print("recent placements:")
        for d in decisions:
            print(f"  {time.strftime('%H:%M:%S', time.localtime(d['ts']))} {d['project']}: {d['why']}")
    return 0


def cmd_balance(args) -> int:
    cfg = load_config()
    root = state_root(cfg)
    ensure_state(root, cfg)
    g = gather(cfg, root)
    snaps = g["snapshots"]
    arch = "any" if args.arch == "any" else normalize_arch(args.arch)
    result = plans(cfg, snaps, arch)
    if args.json:
        print(json.dumps({"hosts": {n: {k: v for k, v in sn.items() if k != "classes"} for n, sn in snaps.items()},
                          "plan": result, "decisions": recent_decisions(root, 10)}, indent=2))
        return 0
    for name, sn in snaps.items():
        print_host(name if name != "local" else "local (this machine)", sn, root)
    print("a new portable job would go to:")
    for r in result:
        print(f"  {r['class']}/{r['latency']}: {r['chosen'] or 'nowhere yet (queued)'}")
        print(f"    {r['explain']}")
    return 0


def cmd_calibrate(args) -> int:
    cfg = load_config()
    root = state_root(cfg)
    ensure_state(root, cfg)
    calib = calibration(root)
    scores = {"local": {"score": bench(args.seconds), "ts": time.time(), **machine_facts()}}
    for name in cfg["hosts"]:
        if args.host and args.host != name:
            continue
        r = Remote(cfg, name, root)
        res = r.ensure_helper() and r.call("bench", r.req(seconds=args.seconds), timeout=60 + 3 * args.seconds)
        if res:
            scores[name] = {"score": res["score"], "ts": time.time(), "cpus": res["cpus"], "arch": res["arch"]}
        else:
            log(f"{name}: unreachable; not calibrated")
    calib.update(scores)
    atomic_write(os.path.join(root, "calibration.json"), calib)
    base = scores["local"]["score"]
    for name, sc in scores.items():
        machine = cfg["local"] if name == "local" else cfg["hosts"][name]
        print(f"{name}: {sc['score'] / 1e6:.2f} M ops/cpu-second, relative speed {sc['score'] / base:.2f} "
              f"(profile speed: {machine['speed']})")
    print("A profile speed that is a number always wins; set \"speed\": \"auto\" to use these ratios. "
          "The benchmark is a pure-Python mix, a rough guide to compile speed.")
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


def owner_pid(requested: str | None) -> int | None:
    """The process whose exit ends the window: --owner-pid, else the calling process unless it is a shell
    (a one-shot shell exits as soon as the command returns, which would end the window at once)."""
    if requested == "none":
        return None
    if requested:
        try:
            return int(requested)
        except ValueError:
            die("--owner-pid takes a pid or 'none'", 2)
    parent = os.getppid()
    if proc_name(parent) in ONE_SHOT_SHELLS:
        log("owner not tracked (the caller is a shell); the window ends after --max or `measure end`. "
            "Pass --owner-pid PID of the long-lived process to end it when that exits")
        return None
    return parent


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
    info = None
    if args.action == "begin":
        try:
            max_seconds = parse_duration(args.max) if args.max else DEFAULT_WINDOW_SECONDS
        except ValueError as exc:
            die(str(exc), 2)
        owner = owner_pid(args.owner_pid)
        info = window_info(args.reason or "", max_seconds, owner)

    def running_jobs() -> tuple[list, list, bool]:
        if is_local:
            jobs = unique_jobs(h for p in local_status(root, cfg)["pools"].values() for h in p["holders"])
            return jobs, [], True
        pr = remote.probe()
        if pr is None:
            return [], [], False
        return unique_jobs(pr["running"]), pr["ci_workers"], True

    if args.action == "sudoers":
        if is_local:
            die("sudoers: pass --host with a configured remote host", 2)
        print(sudoers_rule(hcfg))
        return 0

    if args.action == "status":
        marker = measuring(root, host)
        jobs, workers, reachable = running_jobs()
        print(f"{host}: {'MEASURING ' + describe_window(marker) if marker else 'no measurement window'}")
        if not is_local:
            pr = remote.probe()
            if pr and pr["measuring"] and not marker:
                ended = window_status(pr["measuring"])["ended"]
                print(f"  remote marker only: {describe_window(pr['measuring'])}" + (f" (ended: {ended})" if ended else ""))
            elif not pr:
                print("  remote marker: unreachable")
        print(f"  running broker jobs: {len(jobs)}" + ("" if reachable else " (host unreachable)"))
        for j in jobs:
            print(f"    - {describe_holder(j)}")
        if not is_local:
            print(f"  busy-pattern processes: {len(workers)}")
        return 0

    if args.action == "begin":
        existing = measuring(root, host)
        if existing and not args.force:
            die(f"{host} already has a measurement window: {describe_window(existing)}. "
                "Use `compute measure end` or --force.")
        if remote:
            res = remote.ensure_helper() and remote.call(
                "measure", remote.req(action="begin", marker=hcfg["measure_marker"], info=info, force=args.force))
            if not res:
                die(f"cannot reach {host}; no marker written. Retry when ssh works.")
            if not res.get("ok") and window_status(res.get("existing", {}))["ended"]:
                log(f"replacing an ended window on {host} ({window_status(res['existing'])['ended']})")
                res = remote.call("measure", remote.req(action="begin", marker=hcfg["measure_marker"], info=info, force=True))
            if not res or not res.get("ok"):
                die(f"remote marker already exists: {describe_window(res['existing'])}. Use --force to take over.")
        atomic_write(local_marker_path(root, host), info)
        forget_sample(root, host)
        jobs, workers, _ = running_jobs()
        print(f"measurement window open on {host}: new jobs queue; light jobs and --ignore-measure jobs are unaffected")
        print(f"  ends after {fmt_secs(info['max_seconds'])}" + (f" or when pid {info['owner_pid']} exits"
                                                              if info["owner_pid"] else ""))
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
        forget_sample(root, host)
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
    r.add_argument("--arch", default="any", choices=["any", "arm64", "aarch64", "x86_64", "amd64"],
                   help="only run on a host with this CPU architecture (default any)")
    r.add_argument("--latency", choices=["interactive", "batch"],
                   help="interactive: an agent waits on the result, prefer the fastest host (default for moderate and light); "
                        "batch: long work that may go to the slower host when the fast one is busy (default for heavy)")
    r.add_argument("--expect", type=float, metavar="SECONDS", help="expected runtime on an idle fast host (placement hint)")
    r.add_argument("--no-fallback", action="store_true", help="fail instead of falling back when the host is unreachable")
    s = sub.add_parser("status", help="slots, queue, measurement windows and load on both Macs")
    s.add_argument("--json", action="store_true")
    b = sub.add_parser("balance", help="per-host load, running jobs, and where a new job would be placed")
    b.add_argument("--arch", default="any", choices=["any", "arm64", "aarch64", "x86_64", "amd64"])
    b.add_argument("--json", action="store_true")
    c = sub.add_parser("calibrate", help="benchmark each host and report relative per-CPU speed")
    c.add_argument("--host")
    c.add_argument("--seconds", type=float, default=1.5)
    m = sub.add_parser("measure", help="exclusive measurement window on a host")
    m.add_argument("action", choices=["begin", "end", "status", "sudoers"])
    m.add_argument("--host", help="a configured host name (default: compute.default_host), or local")
    m.add_argument("--reason")
    m.add_argument("--wait", type=int, metavar="SECONDS", help="begin: wait for running jobs to drain")
    m.add_argument("--max", metavar="DURATION", help="begin: longest the window may last, e.g. 90m or 3h (default 3h)")
    m.add_argument("--owner-pid", metavar="PID",
                   help="begin: the window ends when this process exits (default: the caller unless it is a shell; 'none' to disable)")
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
    if args.cmd == "balance":
        return cmd_balance(args)
    if args.cmd == "calibrate":
        return cmd_calibrate(args)
    return cmd_measure(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
