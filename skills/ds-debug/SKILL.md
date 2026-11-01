---
name: "ds-debug"
description: "Use when a test fails unexpectedly, runtime behavior is wrong, or a flaky failure needs a reproducible cause."
---

# Find the cause, then fix it

1. Reproduce it. Write down the exact command or steps, what you expected, and what happened. Read the whole error.
2. Pick one hypothesis and decide what you would see if it were true. Run the cheapest check that tells you, changing one thing at a time. Compare with a working case when you have one.
3. After two wrong hypotheses, recheck inputs, versions, configuration, and what actually ran. After three, write down what you've ruled out and switch methods, for example by bisecting or comparing with a known-good build. If that fails too, mark the item blocked with your notes and move on. Ask only for a specific missing input or decision.
4. Fix the cause, not the symptom. Add a regression test with ds-tdd and remove temporary logging.

A missing service, bad credentials, a full disk, or an overloaded host is an environment problem, not a code bug. Report it as a blocker the way ds-work describes instead of coding around it.

When a flaky test covers code you didn't touch, rerun it once. If it passes, note it as a follow-up and move on. When it covers code you changed, find the shared state, timing, or ordering behind it, and don't hide it with retries or sleeps.
