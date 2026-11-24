---
name: "ds-security"
description: "Use when checking dependencies for vulnerabilities, patching vulnerable dependencies, or when a security review or codebase audit is requested."
license: "MIT; includes ideas adapted from Cloudflare's MIT-licensed security-audit-skill. See LICENSE and NOTICE."
---

# Security maintenance and review

Match the work to the request; updating dependencies does not start an audit.

## Choose the work

- **Dependency maintenance:** inventory resolved versions, check advisories, apply requested updates, and run normal checks via [the dependency procedure](references/dependencies.md). Checks are read-only; patch requests authorize source and lockfile edits.
- **Focused review:** inspect the named change, component, or finding, trace reachable impact, and suggest the smallest fix; edit only if requested.
- **Codebase audit:** agree scope, set a budget before open-ended review, and follow [the audit procedure](references/audit.md). Work alone unless delegation is requested; write report files only when asked.

## Run the right checks

For ordinary checks, use the repository's package manager, build, test, output, and permission rules. Run focused checks while editing and required checks once afterward. Do not impose audit-only OS sandboxes or caps merely because the task concerns security. Lockfile and advisory scans never replace build or behavior checks.

Inspect install hooks before running untrusted packages. Isolate suspected malicious code or exploits from real credentials, data, shared services, and external targets with dummy inputs and matching containment (including memory/time caps for exhaustion tests). If required containment is unavailable, skip that check, continue safe source analysis and independent checks, and report the missing control. Never relabel an exploit as an ordinary test or probe live systems.

## Decide what the evidence supports

Establish input control, reachable path, failing guard (callers, framework, deployment), affected resource, and unauthorized effect. Missing hardening alone is a recommendation.

A complete source trace can prove a defect without execution; distinguish source analysis from executed checks. Keep unresolved deployment facts or incomplete paths as open questions with a next check. Deduplicate by root cause, separate advisory severity from exploitability, and reuse unchanged results. After a fix, run a regression and required checks; after two failed environment fixes, report the blocker and finish independent work.

Report changes or findings, checks, open questions, and reviewed scope. A clean scan means no known advisories in that scan, not a secure app.
