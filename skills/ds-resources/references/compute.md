# compute: shared slots for heavy work

`scripts/compute.py` is a standard-library scheduler and load balancer. Slots are `flock` semaphores in a state directory, so a crashed job frees its slot at once. With remote hosts configured in the resource profile, `--where auto` places each job given `--sync DIR` on whichever host would finish it soonest, over ssh and rsync. It only governs jobs started through it. Python 3.9+; the remote host needs only `python3`, `ssh`, and `rsync`.

## Capacity, slots, and `COMPUTE_JOBS`

Each host (the local machine included) has a pool of slot **units**; a heavy job takes 2 units, a moderate job 1, a light job none (profile `classes` can change the weights). With no profile, `compute` is local-only with one heavy or two moderate jobs per four CPUs. `COMPUTE_JOBS` is the thread count a job of that class should use on that host: CPUs minus 2 for heavy, a third of the CPUs for moderate, 2 for light by default; a profile sets it per host and class, and `CARGO_BUILD_JOBS` follows it unless already set.

**Slots bound real CPU use only if the command honors `COMPUTE_JOBS`.** Pass `-j "$COMPUTE_JOBS"` to make, ninja, cargo (`--jobs`), and test runners (`--test-threads`, `-n`, `--jobs`); a command that spawns its own all-core pool oversubscribes the host however few slots are in use. Size units and jobs together: units times threads per job can exceed the CPU count on purpose, but then the host runs hot.

## Placement

`--where auto` ranks every eligible host by **estimated finish time** and takes the best one with a free slot; if none has a free slot (or all are in a measurement window) the job queues. For each host: `finish = sync + work x max(1, (load + recent starts + job threads) / cpus) / speed`.

- `load` is the 1-minute load average, sampled on the host and reused for `balance.cache_seconds` (5 s) by every process. `recent starts` adds the threads of jobs the broker started in the last `balance.recent_seconds` (90 s), fading linearly, because the load average lags and agents starting together would otherwise all pick the same host.
- `speed` is a per-logical-CPU factor from the profile (the fast machine 1.0, an older machine perhaps 0.45), or `"auto"` to use `compute calibrate` results. The profile number always wins over a calibration.
- `work` is the expected runtime on an idle speed-1.0 host: `--expect SECONDS`, else `balance.work_seconds` (light 5, moderate 60, heavy 600). Remote hosts add `sync`: the last measured rsync time for that job directory, else `balance.sync_default_seconds`, so small jobs stay local.
- The local estimate is multiplied by `balance.local_bias` (0.8 interactive, 0.9 batch), so near-ties go local.
- **`--latency interactive|batch`** (default interactive for moderate and light, batch for heavy). Interactive work, which an agent is waiting on, takes the fastest estimate. Batch work (full suites, fuzz campaigns, proofs, overnight sweeps, toolchain builds) leaves a host's `interactive_reserve` units free for interactive jobs, so it moves to the other host when the fast one is busy; the reserve is waived when the other host is `balance.batch_remote_ratio` (6) times slower or unusable.
- **`--arch any|arm64|x86_64`** (default any) restricts the job to hosts of that CPU architecture (`arch` in the profile; the local machine's is detected). A job pinned to another host's architecture needs `--sync`. Use `--arch` rather than naming a host so the broker can still balance among matching hosts. `--where HOST` and `--where local` pin a job regardless of load.
- An optional `max_norm_load` per host removes it while load per CPU is above that value.
- A host in a measurement window, or unreachable (retried after `balance.down_seconds`), is skipped; other hosts keep working.

`compute balance` shows each host's load (raw and per CPU), speed, free capacity (free CPUs times speed), running jobs with their thread counts, and where a new heavy/batch, moderate/interactive, and heavy/interactive job would go and why. `compute status` shows the same hosts plus queues and the last placements (also in the state directory's `placements.jsonl`).

## Choosing a class

Heavy is a whole-workspace build or test run, fuzzing, or formal verification. Moderate is one package or test shard, a lint, or a typecheck. Light is a quick check. Slots count only jobs started through `compute`.

## Commands

```sh
compute run --class heavy -- cargo test --workspace
compute run --class heavy --sync . --artifacts reports/out.json -- cargo test -j "$COMPUTE_JOBS"
compute run --class moderate --sync . --arch x86_64 -- pnpm test      # any host with that CPU type
compute run --class heavy --latency batch --expect 7200 --sync . -- ./fuzz.sh
compute status [--json]
compute balance [--arch A] [--json]
compute check-profile PATH
compute calibrate [--host HOST]
compute measure begin --host HOST --reason "baseline" --wait 1800     # later: compute measure end --host HOST
```

- **Queueing:** local jobs wait first-in, first-out per pool (a job pinned elsewhere or held back is not counted ahead of anyone) and prints `queued behind N jobs`, then `waited Ns`. Ctrl-C or TERM releases the slot and signals the job's process group. If the broker itself is killed, the job keeps its slot until it exits.
- **Where a job runs:** `--where auto` (default) uses Placement above; without `--sync` a job can only run locally. `--where local` never leaves this machine. `--where HOST` waits for that host's slot and falls back to the local queue if the host is unreachable, unless `--no-fallback`. Light jobs run locally unless `--arch` requires another host.
- **Portable means architecture-independent.** The remote host may have a different CPU architecture; don't use it to produce binaries for this machine. `--artifacts` are paths relative to `DIR`, copied back even when the job fails.
- **Exclusive resources:** Pass `--resource NAME` for a moderate or heavy job that needs an exclusive cache or service on its chosen host. The broker tries the resource before reserving CPU slots, and releases it if admission fails or the job exits. A host profile can also declare `command_resources`, a map from a distinctive literal command fragment to a resource name. The remote helper also reads `command-resources.json` under its configured root so it can enforce the same rule for older clients. Use the same name for all jobs that share the underlying resource. `compute status` shows held resources, and waiting jobs log when the resource is busy. Keep the underlying tool's own lock in place for jobs launched outside the broker.
- **Remote runs** rsync `DIR` (with `--delete`) to `<root>/jobs/<project>/<dir-name>/` and run the command in the matching subdirectory. Project and dir-name come from `~/Workspaces/<project>/...` or `~/Workspaces/worktrees/<project>/<name>`, else from the parent and directory names; override with `--project` and `--name`. Excluded by default: `target/ node_modules/ .git/ .cargo-targets/ .venv/ __pycache__/ .next/ .turbo/` and top-level `build/ out/ cache/ dist/ reports/ tmp/`. Directory symlinks that point outside `DIR` are copied as real files. Add rules with `--include/--exclude` or a `.compute-sync` file in `DIR` with one rsync filter rule per line; to keep only `.git/HEAD`, write `+ .git/`, `+ .git/HEAD`, `- .git/**`. Remote stdin is `/dev/null`.
- **Remote environment:** `CARGO_TARGET_DIR=<root>/cargo/<project>/<dir-name>`, `TMPDIR=<root>/tmp/<project>/<dir-name>`, `COMPUTE_JOBS`, `COMPUTE_CLASS`, `COMPUTE_HOST`, `COMPUTE_PROJECT`, `COMPUTE_JOBDIR`, and `path_prepend` entries in front of `PATH`. Then `<env_dir>/default.sh` and `<env_dir>/<project>.sh` on the remote host are sourced (with `set -a`), so a project can set its toolchain: `printf '%s\n' 'export RUSTUP_TOOLCHAIN=1.91.0' > <env_dir>/<project>.sh`. Job directories persist for incremental builds; delete finished ones by literal path.
- **Measurement windows:** `begin` writes the host's `measure_marker` (remote) and a local marker, and reports running jobs and processes matching `busy_pattern`; `--wait SECONDS` blocks until they drain (exit 3 on timeout; plain `begin` also exits 3 while jobs run; an unreachable host never counts as drained). While a window is open, `--where auto` routes new heavy and moderate jobs to the other hosts (they queue only if none is left); jobs pinned with `--where` wait; light jobs and `--ignore-measure` jobs are unaffected. Locks left by an older profile's pools still count as running jobs. `end` removes both markers. Use `--ignore-measure` only in the job that owns the window.
- **Windows expire by themselves.** `begin` records the owner (`--owner-pid PID`, default the calling process unless it is a shell, whose exit would end the window at once; `none` disables) and a maximum (`--max 90m`, default 3h, units required). A window whose owner has exited (checked on the host it was recorded on, with the process start time guarding against pid reuse) or that passed its maximum counts as ended: the next `compute` command logs it and clears the local and remote markers, and `begin` replaces an ended window without `--force`. `status`, `balance`, and `measure status` show the owner's liveness and the time left. A window recorded on another host is judged by its maximum only.
- **Pausing other services** on a host (for example CI runners) is optional. `pause_commands` and `resume_commands` in the profile are run over ssh by `begin --pause` and `end --resume`; `sudo` always gets `-n`, so no password is ever requested or sent. `compute measure sudoers --host HOST` prints a NOPASSWD rule covering exactly those commands for the owner to review and install.

## Profile

Settings live in the `compute` object of the resource profile (`profiles/default.json` in a bundle; `COMPUTE_PROFILE` selects another file; `COMPUTE_STATE` overrides the state directory). Every field is optional:

```json
{
  "scratch": "/path/to/build-volume",
  "compute": {
    "state": "/path/to/state",
    "default_host": "builder",
    "local": {
      "slots": {"shared": 6},
      "classes": {"heavy": ["shared", 2], "moderate": ["shared", 1]},
      "jobs": {"heavy": 10, "moderate": 4, "light": 2},
      "speed": 1.0,
      "arch": "arm64",
      "interactive_reserve": 2,
      "max_norm_load": null
    },
    "balance": {"local_bias": {"interactive": 0.8, "batch": 0.9}, "cache_seconds": 5, "recent_seconds": 90,
                "batch_remote_ratio": 6, "sync_default_seconds": 10,
                "work_seconds": {"light": 5, "moderate": 60, "heavy": 600}},
    "hosts": {
      "builder": {
        "ssh": "builder",
        "python": "/usr/local/bin/python3",
        "root": "~/compute",
        "env_dir": "~/compute/env",
        "slots": {"shared": 4},
        "classes": {"heavy": ["shared", 2], "moderate": ["shared", 1]},
        "jobs": {"heavy": 12, "moderate": 6, "light": 2},
        "speed": 0.45,
        "arch": "x86_64",
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

The old `local.slots: {"heavy": 1, "moderate": 2}` format is rejected with a message; use units as above. `speed` may be `"auto"` after `compute calibrate`, a quick pure-Python benchmark in CPU-time that is only a rough guide to compile speed.

State directory order: `COMPUTE_STATE`, `compute.state`, `<scratch>/.compute` (refused if that volume is unavailable), then `$XDG_STATE_HOME/dsstack/compute`. Keep real values in the private profile (`.local/policy/resource-profile.json`), never in the public source. The helper copied to a remote host is this same file, refreshed by hash on use.

`run`, `status`, and `balance` show the resolved profile path and state root. `run` reports when an override or per-user fallback is active. Use the shared profile and state for ordinary work and an explicit separate state for isolated tests. `check-profile` validates a profile without creating state or contacting builders. After moving a host path, verify that affected services have loaded the new path and run a small functional check.

## Limits

Slot admission is cooperative: jobs started outside `compute` still load the machines. Remote waiters poll every 5 seconds, so there is no remote queue order. Remote stdout and stderr use separate ssh channels, so their interleaving can differ from a local run. Remote job directories are never garbage-collected. If ssh drops mid-job the remote job is stopped and the exit code is recovered from `<root>/runs/<id>.json`; a started job is never re-run locally.
