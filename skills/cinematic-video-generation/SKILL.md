---
name: cinematic-video-generation
description: >-
  End-to-end cinematic 2D animated video production workflow using Remotion,
  custom visual themes, optional 16-expression animated mascots, official brand
  logos, Fish Speech TTS API or human voiceover drop-in, multi-beat studio SFX,
  automated visual QA, and master CRF 14 1080p rendering. Use when the user
  wants to plan, script, design, animate, or render a cinematic explainer,
  pitch deck video, product launch video, or technical walkthrough.
---

# Cinematic Video Generation

Build studio-grade **cinematic 2D animated videos** (`1920×1080 @ 30 fps`, Remotion + FFmpeg) from initial concept intake through script approval, voiceover generation or ingestion, theme-coherent UI/vector animation, multi-beat studio foley, multi-still visual QA, and `CRF 14` mastering.

---

## Core Operating Principle

Never guess visual style, voiceover mode, mascot presence, or length. Complete **Phase 1 (Discovery Interview)** and obtain user sign-off on **Phase 2 (Script & Visual Plan)** before generating audio files or writing Remotion scene components.

---

## Workflow Phases

### Phase 1 — Mandatory Discovery Interview
Read [./references/discovery-interview.md](./references/discovery-interview.md) and ask targeted intake questions (using `ask_question` for discrete choices plus concise follow-up prompts for assets/IDs) covering all 6 dimensions:

1. **Video Purpose & Target Audience:** Pitch deck, product launch, interactive architecture/security walkthrough, educational explainer, or brand story.
2. **Theme & Custom Color Palette:** Pick a curated preset (`Warm Editorial Cream`, `Midnight Constellation`, `Botanical Sage`, `Crisp Swiss Studio`) or gather exact hex codes (**Primary Canvas**, **Secondary Highlight**, **Brand Signature Accent**, **Ink/Stroke**, **Positive Sage**, **Alert Rust**). Keep a single unified canvas edge-to-edge unless the user explicitly asks for a split layout.
3. **Mascot (`Yes` or `No`):**
   - If **Yes**: Request the user's mascot image (or design brief) to build an expressive 2D vector rig supporting **16 distinct expressions × 16 unique 2D animations** with zero consecutive repeats.
   - If **No**: Use **Pure Editorial / Illustrated Human Cast Mode** (expressive 2D human figures + kinetic typography + brand pedestals).
4. **Logo & Platform Icons:** Request the official brand logo (`png`/`svg`) and any third-party platform/framework icons (`svg`). Render logos cleanly (`mixBlendMode: "multiply"` on light cream/paper canvases or transparent backgrounds—never inside harsh bounding boxes or slapped on device corners).
5. **Voiceover Mode — Fish Speech API vs. Human Voiceover Drop-In:**
   - **Fish Speech / Fish Audio API (`POST https://api.fish.audio/v1/tts`):** Ask which backend `model` header to use (`s2.1-pro` default, `s2.1-pro-free`, `s2-pro`, `s3-pro`, `drama-3`), ask for the voice **`reference_id` (Model ID UUID)**, speaking speed (`0.5–2.0`, default `1.0`), and confirm `$FISH_API_KEY` is set in their environment (never store keys in repo files).
   - **Human Voiceover Drop-In:** Inform the user they can drop their recorded `.mp3`/`.wav`/`.m4a` chapter files into a local folder once the script is approved; normalize them with [./scripts/normalize_audio.py](./scripts/normalize_audio.py).
   - **Silent / Ambient + Kinetic Captions Only:** Calculate timing strictly from scene word count (`~2.4 words/sec`).
6. **Target Length, Chapter Count & Scene Count:** Agree on total duration (`60s` / `15–18 scenes`, `2–3 min` / `35–48 scenes`, `5 min` / `65–80 scenes`, or custom). Target **`3.5–4.5 seconds`** and **`~10–14 words`** per scene so scenes always feel kinetic without rushing.

---

### Phase 2 — Full Script, Visual Plan & Approval Gate
Read [./references/script-and-audio-pipeline.md](./references/script-and-audio-pipeline.md) before drafting the script:
1. Draft the complete **Chapter-by-Chapter, Scene-by-Scene Script Table**:
   - Chapter & Scene ID (`01..N`)
   - Exact spoken narration sentence/clause + word `weight`
   - Literal action metaphor (e.g., physically slicing a red GPS tag off a photo before storing it)
   - Mascot `expression` + `motion` (strictly non-repeating across adjacent scenes `i → i+1`, if Mascot = Yes)
   - Safe layout band (`Band A` headline, `Band B` hero stage, `Band C` / `Side Lanes` mascot foreground)
   - 2–5 multi-beat SFX cues
2. Present the complete script and visual blueprint to the user. Wait for approval (or iterate on edits) before proceeding to Phase 3.

---

### Phase 3 — Voiceover & 12-SFX Studio Foley Pipeline
1. **Generate or Ingest Chapter Audio:**
   - **Fish Speech API:** Write `chapters_script.json` and run [./scripts/generate_fish_tts.py](./scripts/generate_fish_tts.py) (uses `$FISH_API_KEY`, `--model`, `--reference-id`, normalizes to `-16 LUFS / 48 kHz`, outputs `chapter_durations.json`).
   - **Human Drop-In:** Once the user drops their `.mp3`/`.wav` recordings, run [./scripts/normalize_audio.py](./scripts/normalize_audio.py) to convert and loudness-normalize them into `public/audio/part01.mp3..partNN.mp3` and write `chapter_durations.json`.
2. **Synthesize Studio Foley:** Run [./scripts/generate_sfx.py](./scripts/generate_sfx.py) (`--out-dir <project>/public/sfx`) to generate **12 warm WAV SFX** plus a seamlessly loopable **45-second `ambient_bed.mp3`**.

---

### Phase 4 — Cinematic 2D Remotion Engineering
Read [./references/design-system-and-layout.md](./references/design-system-and-layout.md) and (if Mascot = Yes) [./references/mascot-and-animation-kit.md](./references/mascot-and-animation-kit.md):
1. Enforce the **4-Band Zero-Overlap Contract** inside a centered **`1560 × 780` safe-frame** (`1920 × 1080` canvas) with bezier-eased camera drift strictly clamped to **`<= 1.03×`** (`tx <= ±16px`).
2. Eliminate top header chrome (`01 / N` counters, persistent watermarks); place low-profile word-synced captions at bottom center.
3. Implement chapter-distinct parallax atmospheres (clouds, subtle light rays, bokeh dust motes outside text lanes).
4. Map `chapter_durations.json` into `src/data/chapters.ts` using exact per-scene word weights so visuals and captions lock cleanly to the spoken narration.
5. For projects with **`>= 30 scenes`**, spin up a coordinated swarm with strictly disjoint file ownership (`stage-core`, `mascot-cast`, `scenes-a/b/c`, `qa-verifier`)—see [./references/qa-and-rendering-checklist.md](./references/qa-and-rendering-checklist.md).

---

### Phase 5 — Automated Audit & Mandatory Visual Still QA Gate
Read [./references/qa-and-rendering-checklist.md](./references/qa-and-rendering-checklist.md):
1. Run `npx tsc --noEmit` in the Remotion project (must exit `0`).
2. Run [./scripts/audit_video_project.py](./scripts/audit_video_project.py) (`--project-dir <remotion-dir>`):
   - Verifies all 12 SFX + `ambient_bed.mp3` exist (`>0` bytes).
   - Verifies zero UTF-8 mojibake across scenes.
   - If mascot is active, verifies **zero consecutive `expression` or `motion` repeats** from scene `1 → N`.
   - Computes and prints exact midpoint frames for `npx remotion still`.
3. Render **at least 6–14 representative midpoint PNG stills** via `npx remotion still` (covering opening, dense diagrams, complex transitions, dual-label bars, scrolling documents, and closing CTA) and inspect **every still** with image viewing (`read_file`) to confirm zero overlaps, zero clipping, crisp branding, and expressive animation variety before rendering video.

---

### Phase 6 — High-Quality `CRF 14` Master Render & Verification
1. Render the final MP4 with crisp vector fidelity:
   ```bash
   npx remotion render src/index.ts <CompositionId> ../Output_Cinematic.mp4 \
     --codec=h264 --crf=14 --pixel-format=yuv420p \
     --audio-codec=aac --audio-bitrate=192k --concurrency=4
   ```
2. Verify video resolution (`1920×1080`), frame rate (`30/1`), codecs (`h264`/`aac`), and exact audio/video duration match via `ffprobe` before delivering the final file link to the user.
