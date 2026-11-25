# Script Generation, Fish Speech API & Studio Audio Pipeline

---

## 1. Script Pacing & `chapters.ts` Sync Architecture

- **Editorial Reading Rate:** `~145–155 words/minute` (`~2.4 words/second`), targeting **`8–15 words`** per scene so each scene runs cleanly for **`3.5–5.5 seconds`**.
- **Chapter Chunking:** Group every **5–8 scenes** into 1 logical **Chapter (`part01.mp3 .. partNN.mp3`)**. Generating narration per-chapter produces smoother breathing cadence and natural transitions than gluing isolated 3-second snippets.
- **Exact Word-Weight Sync (`ForevernotedPitch.tsx`):**
  Every scene carries a `weight` equal to its spoken word count. At render time, chapter `durationInFrames` is allocated proportionally across scenes so bottom captions, SFX beats, and mascot arrivals align organically with spoken sentences!

### Standard `chapters_script.json` Input Format
Create a clean JSON file right after Phase 2 script approval:
```json
[
  {
    "chapter": 1,
    "title": "Opening & Ownership",
    "text": "Hey, welcome to our studio walkthrough. You do not need to manage servers or complex workflows alone.",
    "scenes": [
      { "id": 1, "label": "Studio Intro", "caption": "Hey, welcome to our studio walkthrough.", "weight": 6 },
      { "id": 2, "label": "Zero Tech Stress", "caption": "You do not need to manage servers or complex workflows alone.", "weight": 11 }
    ]
  }
]
```

---

## 2. Voiceover Option A — Fish Speech / Fish Audio TTS API

Use [../scripts/generate_fish_tts.py](../scripts/generate_fish_tts.py) (stdlib-only Python) to synthesize every chapter from `chapters_script.json`.

### Verified Endpoint & Headers Reference
- **Endpoint:** `POST https://api.fish.audio/v1/tts`
- **Headers:**
  - `Authorization: Bearer $FISH_API_KEY`
  - `Content-Type: application/json`
  - `model: s2.1-pro` *(or `s2.1-pro-free` free tier, `s2-pro`, `s3-pro`, `drama-3`)*
- **JSON Request Payload:**
  ```json
  {
    "text": "Chapter narration text here.",
    "reference_id": "9a9cf47702da476aa4629e2506d4a857",
    "format": "mp3",
    "normalize": true,
    "speed": 1.0
  }
  ```
- **Model Selection Guidance:**
  - `s2.1-pro`: Default balanced studio narration quality.
  - `s2.1-pro-free`: Zero-credit testing/prototyping tier before final VO render.
  - `s3-pro` / `drama-3`: Expressive storytelling / high emotion inflection when the user selects a specific model ID optimized for narrative delivery.
- **Security Rule:** ALWAYS pass API keys via `FISH_API_KEY` environment variable—never hardcode API keys into `.json`, `.py`, or `.ts` files committed to Git.

---

## 3. Voiceover Option B — Human Voiceover Drop-In Workflow

When the user prefers recording their own voice (or hiring a human VO artist):
1. Present the **clean chapter-by-chapter script** (without code clutter) so the speaker can record 1 audio clip per chapter (`part01.wav`, `part02.wav`, etc., or `.mp3`/`.m4a`).
2. Pause coding/rendering until the user drops the audio folder or files into the workspace.
3. Run [../scripts/normalize_audio.py](../scripts/normalize_audio.py) on the dropped files:
   - Loudness-normalizes every chapter uniformly (`ffmpeg loudnorm=I=-16:TP=-1.5:LRA=11`, `48 kHz`, stereo MP3 `192 kbps`).
   - Outputs `public/audio/part01.mp3 .. partNN.mp3` plus `chapter_durations.json` containing exact `durationSec` and `durationInFrames` at `30 fps`.
4. Listen/inspect pacing anomalies and copy the generated `durationSec` / `durationInFrames` into `src/data/chapters.ts`.

---

## 4. 12-SFX Studio Foley & Multi-Beat Trigger Design

Never rely on one repetitive sound at `frame = 0`. Run [../scripts/generate_sfx.py](../scripts/generate_sfx.py) to synthesize **12 warm, non-harsh WAV SFX** + a seamlessly loopable **45s felt-piano `ambient_bed.mp3`** (`volume = 0.055`, ~`-27 dB` under voiceover), and trigger **2–5 synced `sfxCues`** per scene inside `CinematicStage`:

| SFX Name | Character & Acoustic Texture | Best Multi-Beat Scene Triggers |
| :--- | :--- | :--- |
| `whoosh_velvet.wav` | Soft brushed-felt air sweep | Clean scene handoffs, curtain sweeps |
| `whoosh_cinematic.wav` | Wide stereo air/cloud swell | Cloud flights, global map arcs, rapid wipes |
| `pop_wood.wav` | Warm muted marimba/wood tap | Cards, pillars, pedestals appearing sequentially |
| `pop_bubble.wav` | Soft gentle water plop | Thought clouds, typing dots, dissolving rings |
| `boing_soft.wav` | Melodic gentle 2D bounce | Parabolic mascot hops & trampoline hits |
| `chime_warm.wav` | Warm Major-9 bell chord | Gate passes, checkmarks, scene resolutions |
| `sparkle_magic.wav` | Ascending glockenspiel shimmer | Brand stars `✦`, dream reveals, finale |
| `rope_tug.wav` | Organic fiber cinch + slide | Timed to pull start on `edge_tug_slide` |
| `snip_crisp.wav` | Crisp steel scissor *SNIP* | Exact frame where GPS tag/item is sliced off |
| `stamp_thud.wav` | Deep cushioned felt seal impact | `APPROVED`, `REJECTED`, shields locking |
| `alert_soft.wav` | Muted two-tone marimba pulse | Deflections, risk callouts (never jarring!) |
| `page_turn.wav` | Soft cream paper fold rustle | Open book hero, scrolls, policy documents |
