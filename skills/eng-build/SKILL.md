---
name: eng-build
description: >-
  Implementation workflow combining Antigravity-ported pstack discipline, spec-driven
  execution, and parallel subagent orchestration. Use when building features,
  implementing specs/tickets, refactoring, or migrating codebases. Pairs with
  backend and builder.
---

# Engineering Build & Implementation Workflow

Write less, higher-quality code by settling data shapes first, executing in verifiable vertical slices, and proving every unit works.

## Core Principles

Load [references/principles.md](./references/principles.md) before starting non-trivial implementation or refactoring.

## Execution Workflow

### 1. Settle Data Shapes & Seams First
- Name the exact types, schemas, and module boundaries before writing logic (`Foundational Thinking`, `Type System Discipline`).
- Validate external inputs at boundaries; keep core logic pure (`Boundary Discipline`).
- Remove dead code or legacy callers before adding new code (`Subtract Before You Add`).

### 2. Drive Vertical Slices with `tdd`
- Implement one tracer-bullet slice at a time using the global `tdd` skill (`Red -> Green -> Refactor`).
- Assert on observable behavior, not private internals (`Test Behavior, Not Implementation`).

### 3. Parallelize with Antigravity Tools (when work spans independent slices)
- **Single focused slice**: Delegate to `backend` or `builder` via `invoke_subagent`.
- **Parallel independent tickets / specs**: Use `invoke_subagent` with `Workspace: "share"` (or `"branch"` for isolated clones) across the ready frontier, keeping each agent scoped to non-overlapping files.
- **Fan-out pipelines**: Use `run_workflow` for deterministic multi-file sweeps, then aggregate results.
- Keep main-thread summaries tight (`Guard the Context Window`).

### 4. Tighten Before Review
- Apply **Code & Prose Tightening** and **No-Comments Discipline** from [references/principles.md](./references/principles.md): strip dead imports, speculative fallbacks, and narrating comments while preserving existing unrelated docstrings.
- Verify the real artifact runs (`Prove It Works`), then hand off to `eng-review`.
