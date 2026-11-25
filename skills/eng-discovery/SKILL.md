---
name: eng-discovery
description: >-
  Discovery, domain modeling, specification, and architecture planning workflow.
  Use before building non-trivial features to sharpen vague prompts, reframe
  problems, grill design decisions, maintain GLOSSARY.md and ADRs, break specs
  into tracer-bullet tickets, or audit codebase depth. Pairs with architect.
---

# Engineering Discovery & Architecture Workflow

Turn ambiguous ideas into crisp domain models, deep module boundaries, and small verifiable slices before writing production code.

## When to Apply

- Starting a new feature, subsystem, or cross-module change.
- User prompt is ambiguous, high-level, or mixes multiple problems.
- Reviewing or deepening existing module boundaries.

## Workflow Steps

### 1. Sharpen & Reframe (when the problem is fuzzy)
- **Reframe**: If the user can't name what they are building, list the 2–3 distinct problems their words could describe, pick the likeliest with the distinguishing signal, name 8–12 domain terms that change design choices, and restate the goal precisely.
- **Sharpen**: Before executing a big prompt, identify what a senior domain engineer would do unasked, the authoritative primary inputs to inspect first, and the outside check that proves the result works. Settle empirical forks with a quick prototype rather than guessing.

### 2. Grill with Docs (Domain Model & Design Alignment)
- Interview the user relentlessly one focused question at a time until every branch of the design tree is resolved.
- Do the legwork first: inspect existing files, schemas, and git history before asking facts the codebase already answers.
- Maintain a Ubiquitous Language: capture canonical terms in `GLOSSARY.md` (concise definitions so variables, functions, and files stay consistent) and record non-obvious architectural choices in Architecture Decision Records (`ADRs`).

### 3. Prototype Empirical Forks
- When two designs or state models compete, build a minimal throwaway prototype (single self-contained HTML/script or isolated route) to observe real behavior before committing. Keep prototypes isolated from `main`.

### 4. Spec & Tracer-Bullet Tickets
- **To-Spec**: Synthesize resolved decisions into a concise specification naming the exact modules, data shapes, boundaries, and acceptance criteria.
- **To-Tickets**: Slice the spec into small vertical tracer-bullet tasks where each slice touches end-to-end layers, declares its blocking dependencies, and ends in a verifiable state.

### 5. Deepen Codebase Architecture
- Survey modules for shallow wrappers, duplicated logic, or leaky abstractions (Ousterhout's *Philosophy of Software Design*).
- Propose deep-module consolidations: large capability behind a small, testable interface at a clean seam.

## Delegation

- Pair with `architect` for DDD modeling, ADR authoring, deep-module design, and phased roadmaps.
- Hand off settled specs and tracer-bullet tickets to `eng-build` + `tdd`.
