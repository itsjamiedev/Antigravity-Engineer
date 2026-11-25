# Phase 1 — Structured Discovery Interview Guide

Complete this intake cleanly before writing any script or code. Use `ask_question` where multiple-choice options fit cleanly, and follow up briefly for file paths, Fish Speech Model UUIDs, or custom hex codes.

---

## 1. Interview Questions & Options

### Question 1 — Purpose & Target Audience
Ask via `ask_question`:
- **Question:** *"What is the primary purpose and audience of this video?"*
- **Options:**
  1. `(Recommended) Investor / Founder Pitch Presentation` — Clear problem/solution narrative, team ownership, roadmap, architecture, budget, and CTA.
  2. `Product Launch / App Walkthrough` — Onboarding clarity, feature highlights, happy-path user flows, and emotional hook.
  3. `Technical / Security Architecture Deep-Dive` — Literal visual flows for servers, APIs, auth gates, encryption, and scaling.
  4. `Educational / Tutorial / Brand Story` — Conceptual clarity, pacing, memorable visual metaphors, and takeaways.

### Question 2 — Theme & Custom Color Palette
Ask via `ask_question`:
- **Question:** *"Which visual theme and color mood fits this video?"*
- **Options:**
  1. `(Recommended) Warm Editorial Cream` — Warm Cream canvas (`#F5EFE6`), Deep Espresso ink (`#1C1917`), Warm Caramel highlight (`#C97A54`), optional Soft Plum accent (`#3B1848` / `#D8A8F0`).
  2. `Midnight Constellation` — Deep Obsidian Indigo canvas (`#0E111B`), Soft Ivory ink (`#F4EFE6`), Warm Amber Gold (`#E5A95C`), Celestial Violet (`#9C7CF4`).
  3. `Botanical Sage Studio` — Soft Linen canvas (`#F3F5F0`), Forest Ink (`#17261E`), Terracotta (`#C66D51`), Moss Sage (`#467D62`).
  4. `Crisp Swiss Minimalist` — Warm Off-White (`#F8F7F4`), Charcoal (`#141413`), Cobalt Blue (`#2B5B84`), Ochre (`#D18B3B`).
- **Follow-up (Always allow customization):** Ask if the user wants to override any specific hex colors (**Primary Canvas**, **Secondary Accent**, **Brand Accent**, **Ink**, **Success**, **Warning/Alert**) to match an existing brand guideline. Keep one unified canvas background edge-to-edge (no harsh two-tone vertical splits unless explicitly requested).

### Question 3 — Mascot Character (`Yes` or `No`)
Ask via `ask_question`:
- **Question:** *"Should we include an animated 2D mascot guide across the scenes?"*
- **Options:**
  1. `(Recommended) Yes — Use my mascot image (or design one) with 16 expressions & 16 motions` — Keeps viewer engagement high across every scene without consecutive repeats.
  2. `No — Pure Editorial & Human Cast Only` — Uses articulated 2D human figures, brand pedestals, and kinetic diagrams with no mascot character.
- **If Yes:** Ask the user to attach or provide the path to their mascot artwork (or describe its shape, primary fill color, and outline color so we can vectorize an articulated 16-expression SVG rig matching it pixel-for-pixel).

### Question 4 — Logo & Platform Icons
Always ask in text (or alongside artwork upload):
- *"Please drop or link your **official logo** (`png`/`svg`) plus any third-party platform/framework names or logos we should feature (e.g., Apple, Google Play, React, AWS, Stripe, etc.)."*
- Note how light-background logos (`mixBlendMode: "multiply"`) blend invisibly on light themes, or request a transparent PNG/SVG for dark themes (`Midnight Constellation`).

### Question 5 — Voiceover Source (Fish Speech API vs. Human Voiceover Drop-In)
Ask via `ask_question`:
- **Question:** *"How do you want to generate the narration audio?"*
- **Options:**
  1. `(Recommended) Fish Speech / Fish Audio API` — AI studio voiceover from your chosen voice model ID (`reference_id`) and engine (`s2.1-pro` / `s2.1-pro-free`).
  2. `Human Voiceover Drop-In` — We write the script chapter-by-chapter first, pause for you to record, and sync the entire video automatically when you drop the `.mp3`/`.wav` files.
  3. `Visuals + Music + Captions Only (No Voiceover)` — Timed strictly from reading speed (`~2.4 words/sec`) with ambient bed and studio SFX.
- **If Fish Speech API is selected, immediately follow up for these 4 parameters:**
  1. **API Engine (`model` header):** `s2.1-pro` *(default production)*, `s2.1-pro-free` *(free dev tier)*, `s2-pro`, `s3-pro`, or `drama-3`.
  2. **Voice Model ID (`reference_id`):** The UUID of the Fish Audio voice model (e.g., `9a9cf47702da476aa4629e2506d4a857`), or `"none"` to use the default model voice.
  3. **Speaking Speed (`speed`):** `0.5` to `2.0` (`1.0` default editorial pace, `1.05` crisp energetic pace).
  4. **API Key Confirmation:** Remind user to set `FISH_API_KEY` in their shell environment (`$env:FISH_API_KEY = "..."` on Windows / `export FISH_API_KEY="..."` on Unix) rather than pasting secrets into source files.

### Question 6 — Target Video Length, Chapter Count & Scene Count
Ask via `ask_question`:
- **Question:** *"How long should the video be, and roughly how many chapters/scenes should we plan?"*
- **Options:**
  1. `Short Teaser (~60 seconds • 4–5 Chapters • 14–18 Scenes)` — Punchy overview (~140–160 words).
  2. `Standard Explainer (~2–3 minutes • 6–8 Chapters • 35–48 Scenes)` — Deep feature + architecture clarity (~320–450 words).
  3. `(Recommended) Full Pitch / Deep-Dive (~4–5.5 minutes • 10–13 Chapters • 65–80 Scenes)` — Comprehensive investor/client blueprint (~650–820 words).
  4. `Custom Length / Scene Count` — User specifies exact target minutes, chapter count, or scene count.

---

## 2. Scene Pacing Sizing Reference
| Target Length | Spoken Words (~150 WPM) | Chapters | Ideal Scene Count | Avg Seconds / Scene |
| :--- | :---: | :---: | :---: | :---: |
| **45–60 sec** | `115–155` words | `3–5` | `12–18` | `~3.6s` |
| **90 sec** | `215–240` words | `5–6` | `20–26` | `~3.8s` |
| **2.5–3 min** | `375–450` words | `7–9` | `36–48` | `~4.0s` |
| **5–5.5 min** | `740–830` words | `11–13` | `72–82` | `~4.0s` |
