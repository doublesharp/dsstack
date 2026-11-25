# Council procedure

Before reviewing an implementation, fix known issues when authorized and run the relevant checks. Give reviewers the resulting diff and check results.

1. Run independent reviewers in parallel where the host supports it. Give them the same evidence, core questions, criteria, and stop boundary. Add a question suited to a reviewer's strengths when useful. Start fresh, read-only contexts without the coordinator's preferred answer or other reviewers' conclusions.
2. Check findings against source or executable checks as they arrive. Keep the files under review stable while reviewers use the shared checkout. Compare completed answers and combine findings with the same root cause.
3. Recommend an approach based on verified facts. Report any unresolved trade-offs and gaps in reviewer coverage. Fix confirmed problems only when implementation is authorized.
4. If the user asks for agreement, send concrete objections and updated evidence in one fresh follow-up per reviewer, then report agreement or the remaining disagreement. Do not repeat unchanged arguments or expand the roster to force unanimity.

Domain scoring rules belong to the task's rubric. A council provides independent opinions; it does not own a design scorecard, implementation loop, or release permission.
