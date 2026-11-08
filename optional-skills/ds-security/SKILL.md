---
name: "ds-security"
description: "Use when checking dependencies for vulnerabilities, patching vulnerable dependencies, or when a security review or codebase audit is requested."
license: "MIT; includes ideas adapted from Cloudflare's MIT-licensed security-audit-skill. See LICENSE and NOTICE."
---

# Security maintenance and review

Match the work to the request. Updating dependencies does not start a codebase audit. Installing this optional skill does not replace project instructions or host permissions.

## Choose the work

- **Dependency maintenance:** inventory resolved versions, check current advisories, apply requested updates, and run the project's normal checks. Follow the [dependency procedure](references/dependencies.md). A request to check for issues is read-only; a request to patch or update authorizes the corresponding source and lockfile edits.
- **Focused review:** inspect the named change, component, or finding. Trace reachable security consequences and recommend the smallest fix. Modify source only when fixes are requested.
- **Codebase audit:** agree scope from the request, identify important trust boundaries, and review them using the [audit procedure](references/audit.md). State a time or coverage budget before an open-ended audit. Work alone unless independent review or delegation is requested or required. Create report files only when requested.

## Run the right checks

For ordinary checks in the user's working repository, use its package manager, build, test, output, and permission rules. Run focused checks during edits and broader required checks once after the edits they cover. Do not impose an audit-specific OS sandbox or every possible resource limit merely because the task concerns security. Lockfile validation and advisory scans do not replace build or behavior checks.

Before running new or changed third-party packages or code from an untrusted source, inspect their install hooks. For suspected malicious code or exploit reproduction, isolate the check from real credentials, user data, shared services, and external targets. Use dummy inputs and enforce the containment needed for that check, including resource and time bounds for exhaustion tests. If those controls are unavailable, stop that check, continue safe source analysis and unrelated checks, and report the exact missing capability. Never use a routine-test label to evade required containment. Security review alone does not authorize probing live systems.

## Decide what the evidence supports

For each finding, identify who controls the input, its reachable path, the guard that fails, the affected resource, and the resulting unauthorized effect. Check callers, framework protections, and relevant deployment facts before claiming a bypass. Missing hardening alone is a recommendation.

A complete source trace can establish a defect without execution; say which conclusions came from source and which checks ran. An unresolved deployment fact or incomplete path stays an open question with its next check, rather than a confirmed finding. Prioritize demonstrated impact and prerequisites. Distinguish a package advisory's published severity from application exploitability.

Deduplicate by root cause. Reuse prior results only while the relevant code and conditions remain unchanged. Give source locations and a narrow fix; after a requested fix, run a meaningful regression and required project checks. After two failed environment fixes, report the blocker and finish independent work.

Finish with changes or findings, completed checks, unresolved questions, and the scope actually reviewed. A clean advisory scan means no known advisories in that scan, not a secure application. Stop when the requested scope and required checks are complete.
