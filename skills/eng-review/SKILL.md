---
name: eng-review
description: >-
  Code review, adversarial interrogation, PR briefing, and post-session
  retrospective workflow. Use before committing/merging, reviewing diffs, proving
  changes work, or capturing session lessons. Pairs with reviewer and
  tester.
---

# Engineering Review, QA & Shipping Workflow

Close every task with independent verification, evidence-backed review, crisp PR communication, and continuous environment improvement.

## When to Apply

- Reviewing a diff, branch, or pull request.
- Performing pre-commit / pre-merge verification.
- Writing PR summaries or running a post-task retrospective.

## Workflow Steps

### 1. Adversarial Interrogation (`interrogate`)
- Challenge the diff from multiple angles (edge cases, concurrency, error paths, boundary validation, regressions).
- Keep only findings proven by reading concrete code paths or running a reproduction—drop speculative nitpicks.
- Verify no stray debug logs, dead code, or unrequested comments remain (`no-comments` hygiene).

### 2. Independent Two-Axis Review & QA
- **Code Review (`reviewer`)**: Check **Standards Axis** (Fowler smells, minimal diff, performance/accessibility) and **Spec Axis** (every requirement met with zero scope drift).
- **Verification (`tester`)**: Run actual unit/integration/E2E suites and build/typecheck commands (`prove-it-works`). Never report a pass from cached or partial runs without stating exact scope.

### 3. Pull Request Briefing (`pr`)
- Structure PR summaries for fast human review:
  1. **Why**: The user goal and smallest change that meets it.
  2. **Smallest Visual / Diff Map**: Concise diagram or table showing what moved or changed.
  3. **Before / After Evidence**: Exact commands run and observed outputs/screenshots.
  4. **Merge Danger & Blast Radius**: Explicit one-way vs. two-way door assessment and rollback notes.

### 4. Retrospective & Capture (`retro`)
- After tricky or long tasks, identify the highest-leverage friction (missing check, unclear doc, recurring bug) and encode the fix structurally (lint, script, test, or skill/rule update) rather than repeating prose instructions.
