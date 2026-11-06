---
name: "ds-debug"
description: "Use when a test fails unexpectedly, runtime behavior is wrong, or a flaky failure needs a reproducible cause."
---

# Find the cause, then fix it

1. Reproduce the failure with the exact command or steps, expected result, and actual result. Read the full error and compare a working case when available.
2. Choose one hypothesis and the cheapest observation that could disprove it. Change one variable at a time.
3. After two wrong hypotheses, recheck inputs, versions, configuration, and what actually ran. After a third, record what you ruled out and switch methods, such as bisecting or comparing a known-good build. If that also fails, report the specific missing input or decision and stop the affected work.
4. Fix the cause and lock it down with a focused regression check. Prefer a failing test before the fix; if the reproduction is impractical, explain the gap and use the closest executable check. Remove temporary logging.

Missing services, credentials, disk, and overloaded hosts need one or two direct environment fixes, then a blocker report. Do not change product behavior to hide the environment failure.

For a flaky test outside changed code, rerun once and report a follow-up if it passes. For changed code, investigate shared state, timing, or ordering; do not hide failures with retries or sleeps.
