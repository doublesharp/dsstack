# compute: shared slots for heavy work

`scripts/compute.py` is a standard-library scheduler. Local slots are `flock` semaphores in a state directory, so a crashed job frees its slot at once. With a remote host configured in the resource profile, jobs given `--sync DIR` can overflow to it over ssh and rsync. It only governs jobs started through it. Python 3.9+; the remote host needs only `python3`, `ssh`, and `rsync`.

## Classes and defaults

With no profile, `compute` is local-only: 1 heavy slot, 2 moderate slots, light unlimited. `COMPUTE_JOBS` is the CPU count for heavy, a third of it (at least 2) for moderate, and 2 for light; `CARGO_BUILD_JOBS` is set to the same value unless already set. A remote host defaults to one shared pool of 2 units where heavy takes 2 and moderate takes 1. Profiles change all of these.

## Choosing a class

Heavy is a whole-workspace build or test run, fuzzing, or formal verification. Moderate is one package or test shard, a lint, or a typecheck. Light is a quick check. Slots count only jobs started through `compute`.

## Commands

```sh
compute run --class heavy -- cargo test --workspace
compute run --class heavy --sync . --artifacts reports/out.json -- cargo test -j "$COMPUTE_JOBS"
compute run --class moderate --where HOST --sync . -- pnpm test
compute status [--json]
compute measure begin --host HOST --reason "baseline" --wait 1800     # later: compute measure end --host HOST
```

- **Queueing:** a local job waits first-in, first-out per class and prints `queued behind N jobs`, then `waited Ns`. Ctrl-C or TERM releases the slot and signals the job's process group. If the broker itself is killed, the job keeps its slot until it exits.
- **`--where auto`** (default): run locally if a slot is free; otherwise, with `--sync` and a configured, reachable remote host that has a free slot and no measurement window, run there; otherwise queue locally. `--where local` never overflows. `--where HOST` waits for a remote slot and falls back to the local queue if the host is unreachable, unless `--no-fallback`. Light jobs always run locally.
- **Portable means architecture-independent.** The remote host may have a different CPU architecture; don't use it to produce binaries for this machine. `--artifacts` are paths relative to `DIR`, copied back even when the job fails.
- **Remote runs** rsync `DIR` (with `--delete`) to `<root>/jobs/<project>/<dir-name>/` and run the command in the matching subdirectory. Project and dir-name come from `~/Workspaces/<project>/...` or `~/Workspaces/worktrees/<project>/<name>`, else from the parent and directory names; override with `--project` and `--name`. Excluded by default: `target/ node_modules/ .git/ .cargo-targets/ .venv/ __pycache__/ .next/ .turbo/` and top-level `build/ out/ cache/ dist/ reports/ tmp/`. Directory symlinks that point outside `DIR` are copied as real files. Add rules with `--include/--exclude` or a `.compute-sync` file in `DIR` with one rsync filter rule per line; to keep only `.git/HEAD`, write `+ .git/`, `+ .git/HEAD`, `- .git/**`. Remote stdin is `/dev/null`.
- **Remote environment:** `CARGO_TARGET_DIR=<root>/cargo/<project>/<dir-name>`, `TMPDIR=<root>/tmp/<project>/<dir-name>`, `COMPUTE_JOBS`, `COMPUTE_CLASS`, `COMPUTE_HOST`, `COMPUTE_PROJECT`, `COMPUTE_JOBDIR`, and `path_prepend` entries in front of `PATH`. Then `<env_dir>/default.sh` and `<env_dir>/<project>.sh` on the remote host are sourced (with `set -a`), so a project can set its toolchain: `printf '%s\n' 'export RUSTUP_TOOLCHAIN=1.91.0' > <env_dir>/<project>.sh`. Job directories persist for incremental builds; delete finished ones by literal path.
- **Measurement windows:** `begin` writes the host's `measure_marker` (remote) and a local marker, and reports running jobs and processes matching `busy_pattern`; `--wait SECONDS` blocks until they drain (exit 3 on timeout; plain `begin` also exits 3 while jobs run; an unreachable host never counts as drained). While a window is open, new heavy and moderate jobs for that host queue; light jobs and `--ignore-measure` jobs are unaffected. `end` removes both markers. Windows don't expire. Use `--ignore-measure` only in the job that owns the window.
- **Pausing other services** on a host (for example CI runners) is optional. `pause_commands` and `resume_commands` in the profile are run over ssh by `begin --pause` and `end --resume`; `sudo` always gets `-n`, so no password is ever requested or sent. `compute measure sudoers --host HOST` prints a NOPASSWD rule covering exactly those commands for the owner to review and install.

## Profile

Settings live in the `compute` object of the resource profile (`profiles/default.json` in a bundle; `COMPUTE_PROFILE` selects another file; `COMPUTE_STATE` overrides the state directory). Every field is optional:

```json
{
  "scratch": "/path/to/build-volume",
  "compute": {
    "state": "/path/to/state",
    "default_host": "builder",
    "local": {"slots": {"heavy": 1, "moderate": 2}, "jobs": {"heavy": 12, "moderate": 4, "light": 2}},
    "hosts": {
      "builder": {
        "ssh": "builder",
        "python": "/usr/local/bin/python3",
        "root": "~/compute",
        "env_dir": "~/compute/env",
        "slots": {"shared": 4},
        "classes": {"heavy": ["shared", 2], "moderate": ["shared", 1]},
        "jobs": {"heavy": 14, "moderate": 4, "light": 2},
        "path_prepend": ["/usr/local/bin", "~/.cargo/bin"],
        "measure_marker": "~/compute/MEASURING",
        "busy_pattern": "Runner.Worker",
        "pause_commands": [["sudo", "launchctl", "bootout", "system/example.service"]],
        "resume_commands": [["sudo", "launchctl", "bootstrap", "system", "/Library/LaunchDaemons/example.service.plist"]]
      }
    }
  }
}
```

State directory order: `COMPUTE_STATE`, `compute.state`, `<scratch>/.compute` (refused if that volume is unavailable), then `$XDG_STATE_HOME/dsstack/compute`. Keep real values in the private profile (`.local/policy/resource-profile.json`), never in the public source. The helper copied to a remote host is this same file, refreshed by hash on use.

## Limits

Slot admission is cooperative: jobs started outside `compute` still load the machines. Remote waiters poll every 5 seconds, so there is no remote queue order. Remote stdout and stderr use separate ssh channels, so their interleaving can differ from a local run. Remote job directories are never garbage-collected. If ssh drops mid-job the remote job is stopped and the exit code is recovered from `<root>/runs/<id>.json`; a started job is never re-run locally.
