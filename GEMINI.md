# Antigravity Engineering OS — Global Rules

## 1. Interactive Pre-Execution Protocol (Mandatory Before Work)

Unless the request is a simple factual question with no file/code/design changes (or the user explicitly says "run directly without asking"), **ALWAYS pause before planning or editing** and send a concise intake brief covering these 4 items in order:

1. **What We Will Do**: Summarize the planned change or fix in plain language.
2. **Skills & Mandatory Guardrails**:
   - List the exact skills you plan to apply and ask: **"Do you want to change or swap any of these skills?"**
   - **UI Rule (`unslop` Always Locked In)**: On **every** UI/frontend task, **`unslop`** (plus `impeccable` `craft-floor`, `distill`, `polish` baseline) is **ALWAYS active automatically with zero opt-out** so UI is never sloppy — AND explicitly tell the user: *"We're also pairing the `unslop` skill (+ `impeccable` guardrails) on this UI work."* Offer optional pairings (`taste-skill`, `apple-design`, `animate`, `mobile-native`, `stageshow`) for approval.
   - **Animation & Motion Rule**: Whenever working on animations, physics, 3D scenes, interactive SVG explainers, or product UI demos, automatically recommend the matching `motion` skills (**`animate`**, **`anatomy`**, **`apple-design`**, **`mobile-native`**, **`stageshow`**, **`threejs`**) and ask: *"Do you want to use `[recommended skills]`?"*
3. **Sub-Agents Proposal (Asked Before Planning)**:
   - Ask explicitly: **"Do you want to use sub-agents?"**
   - Recommend a **concrete number of specialized sub-agents** (using the simplified roster below), naming each sub-agent, what specific improvements or deliverables it will produce, and which exact skills it will use.
4. **Detailed Plan Confirmation**:
   - Ask: **"Do you want me to write an extremely detailed plan first before starting?"**
   - When the user approves planning, invoke `eng-discovery` (+ `writing-plans` if present in workspace) to deliver a deeply detailed step-by-step plan covering architecture, exact files, sub-agent assignments, skills per step, improvements, and checks before implementation.

Wait for the user's reply to confirm skill choices, sub-agent usage/count, and whether to draft the detailed plan before modifying files. Always close execution with **Prove-It-Works** verification (real tests, linters, typecheck, build, or rendered browser/frame checks) before reporting done.

---

## 2. Global Skill & Subagent Routing Map

| Domain | Global Skill(s) (`~/.gemini/config/skills/`) | Paired Subagent (`~/.gemini/config/agents/`) |
| :--- | :--- | :--- |
| **UI Craft & Anti-Slop** | `unslop` *(mandatory)*, `impeccable`, `taste-skill` | `designer` |
| **Animation, 3D, SVG & Mobile** | `animate`, `apple-design`, `mobile-native`, `stageshow`, `anatomy`, `threejs` | `motion` |
| **Discovery & Architecture** | `eng-discovery` | `architect` |
| **Build & TDD** | `eng-build`, `tdd` | `backend`, `builder` |
| **Debug & Change Safety** | `eng-debug` | `debugger` |
| **Code Review** | `eng-review` | `reviewer` |
| **QA & Test Automation** | `tdd`, `eng-review` | `tester` |
| **Security & RLS Audits** | `security-audit` | `security` |
| **Video & Remotion** | `remotion-best-practices`, `cinematic-video-generation`, `video` | `producer` |
| **Ecosystem & Skill Audits** | `agy-customizations` *(built-in)* | `curator` |

---

## 3. Skill Evaluation Rubric

Before adding or keeping any skill:
1. **Antigravity Compatibility**: Must work natively with Antigravity (`SKILL.md`, `invoke_subagent`, `run_workflow`, `browser`). Reject Cursor-only or Claude-Code-only lock-in unless ported.
2. **Zero Overlap**: Check against existing global skills and custom agents; replace weaker duplicates rather than stacking them.
3. **Progressive Disclosure**: Prefer one router `SKILL.md` with `references/` and `scripts/` over scattered micro-skills.
4. **Local Verification**: Valid `name` + `description` YAML frontmatter, intact relative links, and passing local tests for any bundled scripts.
