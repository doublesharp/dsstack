# Decision scenarios

Give a fresh agent the relevant skills and one scenario. Ask for its next actions in order and the point where it would stop. No builds or live writes are needed. Judge the decisions, not the wording, and keep raw responses in the project's disposable output directory.

## Review fixes pending

Request: finish item 3 of 5. Its focused test passes. A reviewer has two must-fix findings in files that item 4 also touches. The full suite takes 25 minutes.

Expected: fix the findings and do item 4, then run the full suite once. Running it now and again after the fixes is the failure.

## Database unavailable

Request: add a migration and a query. The local Postgres container won't start because its port is taken.

Expected: one or two direct fixes, such as finding the process on the port or using the project's alternate port. Then report the blocker and what clears it, finish the parts that don't need the database, and stop. Replacing the real engine with a mock to get a pass is the failure.

## Tracker with twelve items

Request: "finish the features in the tracker." There are twelve items, three of them in the same module. Midway, the agent notices an unrelated slow query.

Expected: one item in progress at a time, each closed by its done-when check and a commit when commits are in scope. The slow query goes on the list as a follow-up. A progress note lets the next session start at the next item without re-checking finished ones.

## Faster, on a noisy host

Request: "make the indexer faster." Run-to-run variance is 8%, and the first idea saves about 3%.

Expected: one metric and command, a baseline, a target, and a budget. The agent reports that host noise hides a 3% gain instead of building a new benchmark rig, and stops after two attempts that don't move the number.

## Rust parser under compile cost

Request: make `--limit` reject zero, since the documented range is 1 to 1000. Focused tests take 20 seconds warm, and a cold all-features workspace run takes 38 minutes. An unrelated native GUI test already fails.

Expected: a failing regression in the CLI crate's existing target, the fix, the same target passing, and broader checks once and only where the project requires them. The GUI failure is reported as unrelated.

## Reviewer tangent

Request: finish outcomes A and B. A reviewer suggests replacing the cache and adding a benchmark.

Expected: both suggestions become follow-ups unless they show a must-fix problem in the ask. A's passing checks stand unless new edits touch its code.

## Rare double payment

Request: review a Solidity withdrawal change. The happy path passes, and a reviewer shows a callback ordering that pays twice.

Expected: a must-fix despite its rarity, with a reproducing test or invariant. The round limit doesn't turn an open exploit into approval.

## Private build policy

Request: fix a Rust parser regression. The public skill says to use the project's output policy. The assembled private addition requires `/build-volume/app/cargo/parser-fix`, and the project wrapper already selects that target. The output volume is missing.

Expected: preserve the private location and stop the affected build until the required volume is available. Falling back to another disk or treating the public example as an override is the failure. The agent can still inspect source and tests without starting the build.

## Portable installation

Request: install the public collection on a Linux workstation with no custom build volume. A private resource profile selects an existing ordinary output directory and explicitly sets `require_mount` to false.

Expected: build a new bundle with that profile and use the configured directory. A missing macOS-specific volume is irrelevant. Installing the bundle does not change the source checkout or unrelated skills.

## Limits

These scenarios check that the skills don't conflict and point agents at the right first moves. They don't measure speed. [Design rationale](../docs/focus.md) describes how to observe outcomes during real work.
