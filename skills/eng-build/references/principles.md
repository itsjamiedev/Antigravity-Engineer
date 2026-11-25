# Core Engineering Principles (Distilled from pstack)

Read and apply the relevant rules below during implementation and review. Keep only what changes a concrete engineering decision.

## Core

1. **Laziness Protocol**: Bias toward deletion and the smallest change that solves the problem. Resist speculative abstractions, extra layers, or signal plumbing.
2. **Foundational Thinking**: Before writing logic, settle core types, data structures, scaffold-vs-feature order, and what concurrent actors share. Get the data shape right so downstream code becomes obvious.
3. **Redesign from First Principles**: When integrating a new requirement into an existing design, reshape it as if the requirement had been foundational from day one rather than bolting on flags or patches.
4. **Attack the Premise**: When 2+ fixes sharing one assumption fail the same gate, stop coding. Write the assumption down and test it directly before writing another fix.
5. **Subtract Before You Add**: Remove dead weight, redundant validators, and stale stubs first, then build on the simpler base.
6. **Minimize Reader Load**: Count indirection layers between question and answer and hidden state in the reader's head. Collapse single-caller wrappers and shrink mutable scope.
7. **Outcome-Oriented Execution**: During planned rewrites/migrations with explicit phase boundaries, converge directly on the target architecture instead of maintaining throwaway compatibility shims.
8. **Experience First**: Choose user delight and clarity over implementation convenience; ship fewer polished flows over many rough ones.
9. **Exhaust the Design Space**: For novel interactions or high-stakes architecture with no precedent, compare 2–3 prototypes side by side before committing.
10. **Build the Lever**: For repetitive or multi-step work (migrations, checks, audits), build a repeatable script, codemod, or check so reviewers can rerun the proof.

## Architecture

11. **Model the Domain**: Encode stateful or branching rules in a structure (state machine, typed union, lookup table, reducer) rather than scattered `if/else` chains.
12. **Boundary Discipline**: Validate and guard at system boundaries (CLI, HTTP/RPC, config, external APIs, IPC); trust internal types and keep core business logic pure.
13. **Type System Discipline**: Make illegal states unrepresentable, brand semantic primitives, parse untrusted inputs at boundaries, exhaustively handle variants, and derive types from authoritative schemas.
14. **Make Operations Idempotent**: Design commands, migrations, and lifecycle steps so partial or repeated runs converge to the same end state.
15. **Migrate Callers, Then Delete Legacy APIs**: Migrate every caller and delete the deprecated API in the same wave rather than preserving compatibility layers indefinitely.
16. **Separate Before Serializing Shared State**: Eliminate shared mutable state first; serialize structurally only when a single shared writer is a genuine invariant.

## Verification

17. **Prove It Works**: Never claim done from compilation, static inspection, or "looks right." Verify against the real running artifact (tests, HTTP calls, CLI output, browser render, or diff inspection).
18. **Fix Root Causes**: Trace every symptom to the first place the system went wrong and fix it there. A defensive guard is only a fix when the state it catches is legitimate.
19. **Sequence Verifiable Units**: Break sweeps and migrations into small units that each end in a green, verifiable state; verify each unit before starting the next.
20. **Test Behavior, Not Implementation**: Assert on observable user/caller contracts so tests break when behavior regresses and stay green across internal refactors.
21. **Explain the Number**: Before trusting or reporting a benchmark, latency, throughput, or eval metric, identify what limits it and confirm you measured the actual workload.

## Delegation & Meta

22. **Guard the Context Window**: Route bulk reads, searches, and multi-file sweeps to subagents; keep concise, decision-ready summaries in the main thread.
23. **Never Block on the Human**: Proceed on reversible implementation work, present the verified result, and reserve confirmation pauses for irreversible/destructive actions or genuinely ambiguous product/UI choices.
24. **Encode Lessons in Structure**: Turn recurring mistakes into lints, schema checks, tests, or scripts rather than adding more prose rules.

## Code & Prose Hygiene

- **Code/Prose Tightening**: Remove filler words, tautologies, dead helpers, defensive fluff around impossible states, and speculative fallbacks.
- **No-Comments Discipline**: Keep existing unrelated docstrings/comments intact, and avoid noisy narrating comments ("increment counter", "return result"). Write comments only for non-obvious invariants, edge-case *why*s, or required API docstrings.
