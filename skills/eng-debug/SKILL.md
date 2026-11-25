---
name: eng-debug
description: >-
  Root-cause debugging, change safety, and codebase archaeology workflow. Combines
  git/PR history investigation (why), runtime breakage proof (blast-radius), and
  deterministic reproduction loops. Use for hard bugs, regressions, performance
  issues, or risky changes. Pairs with debugger.
---

# Engineering Debug & Change-Safety Workflow

Never patch symptoms blindly. Prove the cause with a tight reproduction loop, understand historical intent, and prove blast radius with executed checks.

## When to Apply

- Diagnosing bugs, intermittent failures, race conditions, or performance regressions.
- Investigating why a module, flag, or workaround exists before changing it (`why`).
- Assessing what a small-looking change could break (`blast-radius`).

## Workflow Steps

### 1. Archaeology (`why`) — Before Touching Unfamiliar Code
- Answer from the historical record, not guesswork: inspect `git log -S`, `git blame`, commit messages, ADRs, and PR descriptions that introduced and modified the behavior.
- Clearly separate cited facts from inferences and call out what the record does not answer.

### 2. Build a Tight Feedback Loop (1–5s Repro)
- Spend upfront effort building a fast, deterministic reproduction (failing unit test, curl/script replay, or headless browser check) before editing production code.
- Never guess-and-edit without a failing check that turns green only when the bug is fixed.

### 3. Hypothesize, Bisect & Attack the Premise
- Formulate a specific falsifiable hypothesis and test one variable at a time (use `git bisect`, targeted logs, or runtime traces).
- **Attack the Premise**: If 2 fixes sharing one assumption fail the same check, stop immediately, write down the shared premise, and test that premise directly before writing a third fix.

### 4. Prove Blast Radius (`blast-radius`)
- Trace all callers, shared state, schemas, and side effects touched by the planned change.
- Prove safety by **running** tests, typechecks, or reproduction scripts against affected paths—never assert "it looks safe" by reading alone.

### 5. Minimal Root-Cause Fix & Regression Lock
- Fix the defect at the first place the system went wrong (`Fix Root Causes`).
- Keep the diff surgical and leave a regression test that stays red without the fix and green with it.

## Delegation

- Pair with `debugger` for complex repro loops, memory/motion profiling, concurrency races, and multi-way merge conflicts.
