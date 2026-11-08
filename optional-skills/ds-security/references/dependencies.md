# Dependency maintenance

Start with the owning package, runtime pin, package manager, manifests, lockfiles, and existing update policy. Inspect Git state so unrelated work survives. Include runtime, development, build, and CI dependencies in the inventory; a development dependency may execute during builds or releases.

Use the ecosystem's advisory tooling and primary advisory or maintainer sources. Record which resolved versions are affected, the patched range, whether a dependency is direct or transitive, and what consumes it. Check freshness: a cached or offline result is not a current advisory check. If the registry or advisory service is unavailable after one or two direct attempts, report that gap and continue checks that can run locally.

For requested patches, prefer the smallest supported update that fixes the advisory and meets the project's compatibility policy. Avoid unrelated major upgrades. For a transitive issue, update the owning direct dependency first; use a scoped override only when compatible and justified. Do not suppress an advisory to make the scan green. If no supported patch exists, explain the affected path and an actionable mitigation or follow-up.

Regenerate lockfiles through the owning package manager. Review the resolution diff for unexpected package, source, integrity, or lifecycle-hook changes before installation. Honor registry and network permissions; inspect suspicious packages rather than running their hooks with host secrets. Do not delete a lockfile or shared dependency tree as a routine repair.

Run the checks that cover the changed consumer, plus the project's required build, type, lint, and behavioral checks. Use the existing output policy. Frozen or immutable lockfile checks establish resolution consistency only. Recheck advisories after the updates, covering both production and development dependencies when supported, and explain any excluded scope.

Report changed versions, remaining advisories, and actual checks. Keep an advisory's published severity visible even when runtime reachability is uncertain; explain the uncertainty instead of claiming the package is harmless. A passing audit does not prove that a deployment uses the new lockfile, that an executable bundled its dependencies anew, or that code has no vulnerabilities.
