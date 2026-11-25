# Mascot 16-Expression × 16-Motion System (Plus Non-Mascot Mode)

---

## 1. Mode Switch: Mascot = `Yes` vs. `No`

- **If Mascot = `Yes`:** The mascot appears and moves naturally in **every scene** with **ZERO consecutive repeats** of either `expression` OR `motion` across `Scene 01 → Scene N`.
  - When adapting to the user's mascot upload: vectorize a crisp inline SVG rig matching their mascot's exact silhouette, body fill color, thick stroke color, limb style, and silhouette details so its arms, legs, eyes, cheeks, mouth, and props animate smoothly at 30 fps.
- **If Mascot = `No` (`Pure Editorial Mode`):** Replace `<MascotStageActor />` with expressive **Illustrated Human Cast** figures (`Founder`, `Engineer`, `Specialists`, `Couple`, `Security Guardian`, `Reviewer`), thought-bubble clouds (`o · o · O`), animated data packets, and floating optical spotlights inside the same 4-Band Zero-Overlap grid.

---

## 2. The 16 Charming 2D Mascot Expressions

Retire harsh, angry, or gritted-teeth mouths. Give every expression **warm rosy cheeks**, **white eye specular glints** (for open-eye expressions), **expressive eyebrows**, and **natural periodic blinking** (`~3 frames` every `~95 frames`):

| # | `MascotExpression` ID | Eyes & Glints | Brows & Mouth | Animated Micro-Emote Prop |
| :-: | :--- | :--- | :--- | :--- |
| 1 | `beam` | Wide happy ovals + double glints | Soft lifted brows + warm open smile | Subtle sparkle aura |
| 2 | `starry_eyed` | Twinkling 4-point stars inside pupils | High wonder brows + delighted grin | Orbiting 4-point `✦` stars |
| 3 | `wink_cheer` | Left oval + right happy wink arc (`◠`) | Playful asymmetric brow + upbeat smile | Floating music note `♪` |
| 4 | `curious_tilt` | Attentive ovals shifted toward target | One intrigued lifted brow + small `"o"` | Floating `?` glyph |
| 5 | `deep_think` | Half-lidded upward gaze | Concentrated soft brow + petite ponder | Rising `o · o · O` mini cloud |
| 6 | `proud_smug` | Happy upward crescents (`^ ^`) | Relaxed confident brows + satisfied grin | Golden corner glint |
| 7 | `focused_effort` | Earnest focused ovals looking at task | Angled determined brows + cute grin | Single animated effort sweat drop |
| 8 | `excited_wow` | Large gleaming sparkle eyes | High arches + big open `"D"` grin | Exclamation spark `!` |
| 9 | `relieved_sigh` | Peaceful downward curves (`◡ ◡`) | Soft calm brows + serene smile | Soft exhale puff |
| 10 | `heart_eyes` | Two warm colored hearts (`♥ ♥`) in eyes | Adoring arches + sweet `"ω"` smile | Floating mini heart |
| 11 | `protective_brave` | Steady courageous ovals | Heroic confident brows + firm smile | Glowing barrier ring |
| 12 | `surprised_gasp` | Wide round saucer eyes | High startled brows + small `"O"` | Twin alert rings |
| 13 | `playful_cheeky` | Bright side-glancing ovals | Mischievous brow + cute grin + tiny blep | Cheeky wink flash |
| 14 | `celebrate_joy` | Joy-squinted arcs (`◠ ◠`) | Ecstatic brows + wide cheering laugh | Confetti `✦ ♥` burst |
| 15 | `gentle_empathy` | Soft glistening warm ovals | Empathetic tilted brows + caring smile | Soft halo glow |
| 16 | `salute_ready` | Crisp attentive forward ovals | Confident brows + crisp smile | Right-hand temple salute pose |

---

## 3. The 16 Unique 2D Mascot Motions

Never repeat the exact same `motion` two scenes in a row. Implement each motion inside `MascotStageActor` with authentic 2D squash-and-stretch physics and distinct props:

| # | `MascotMotion` ID | Choreography, Physics & Props |
| :-: | :--- | :--- |
| 1 | `book_pop_out` | Springs upward out of logo/document with sparkle trail & soft ground landing puff |
| 2 | `curtain_sweep` | Holds outer tassel of a warm cream veil, sweeping cleanly across Band C |
| 3 | `cloud_ride` | Surfs smoothly atop a miniature fluffy cream-and-espresso cloud with star dust |
| 4 | `peek_and_point` | Slides smoothly in from outer margin/Side Lane and points toward hero element |
| 5 | `double_hop_step` | Two rhythmic parabolic hops in Band C (`scaleX/Y` stretch & squash + dust puffs) |
| 6 | `edge_tug_slide` | Anchored in Side Lane / outer margin leaning backward on an **outer-edge-only** rope |
| 7 | `orbit_glide` | Smooth bezier glide along clear lower arc trailing luminescent dots |
| 8 | `sprint_track` | Animated brisk running leg cycle across Band C with 2D cartoon speed lines |
| 9 | `tiptoe_inspect` | Delicate tiptoe step across Band C holding a miniature magnifying glass upward |
| 10 | `spin_twirl` | Energetic mid-air 360° 2D spin (`scaleX` cosine flip + arm flare + star ring) |
| 11 | `parachute_float` | Descends gently under a miniature striped caramel/cream parachute canopy |
| 12 | `trampoline_bounce` | Bounces rhythmically atop a miniature drawn springboard inside Band C |
| 13 | `shield_stance` | Defensive wide stance holding a checkmark shield with expanding barrier ripple |
| 14 | `laser_snip_action` | Steps beside cutter beam with animated gleaming steel scissors snipping tag off |
| 15 | `victory_dance` | Rhythmic joyful side-to-side celebratory bounce with arms raised + confetti stars |
| 16 | `book_settle_wave` | Hops gently onto logo bookmark notch (or closing pedestal) & waves farewell |

---

## 4. Non-Repetition Rule (`scenes-a/b/c`)
When designing the full scene table in Phase 2, ensure mathematically:
```text
For every scene i from 1 to N - 1:
  scene[i].expression !== scene[i + 1].expression
  scene[i].motion     !== scene[i + 1].motion
```
Validate this automatically using `scripts/audit_video_project.py` before rendering!
