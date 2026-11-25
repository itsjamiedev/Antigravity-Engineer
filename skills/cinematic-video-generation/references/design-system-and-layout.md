# Cinematic 2D Design System & 4-Band Zero-Overlap Contract

---

## 1. The Hard 4-Band Zero-Overlap Contract (`1560 × 780` Safe-Frame)

Render all video compositions at **`1920 × 1080 @ 30 fps`**. Keep every visual stage strictly centered inside **`SAFE_W = 1560`**, **`SAFE_H = 780`** (`left: 180`, `top: 90`, leaving `180px` horizontal margins, `90px` top margin, and `210px` bottom breathing/caption space).

```text
+-----------------------------------------------------------------------------------+  y = 0
| BAND A (y: 12 .. 165) — EXCLUSIVE HEADLINE CORRIDOR                               |
|   EditorialHeadline (kicker + serif title + subtitle).                            |
|   ZERO mascot bodies, speech bubbles, jump apexes, or ropes allowed above y = 178 |
|   whenever a scene displays an EditorialHeadline (`hasHeadline !== false`).       |
+-----------------------------------------------------------------------------------+  y = 175
| LEFT SIDE LANE | BAND B (y: 185 .. 565) — HERO STAGE & HUMAN CAST | RIGHT SIDE   |
| (x: 40..210)   |   Pedestals, HumanFigures, WorldMap, Scrolls,    | LANE          |
| Mascot side    |   ServerTowers, PhoneUI, Budget Drawers.         | (x:1350..1510)|
| zone           |   Min 24px gap between all cards/labels/badges.  | Mascot side   |
|                |   Dual-label headers MUST use space-between.     | zone          |
+-----------------------------------------------------------------------------------+  y = 575
| BAND C (y: 585 .. 745) — EXCLUSIVE MASCOT FOREGROUND WALKWAY                      |
|   Mascot rests/walks/runs at y = 635..710.                                        |
|   Outer-Edge Rope Rule: Pull ropes attach ONLY to outer rims/tabs, NEVER text!    |
+-----------------------------------------------------------------------------------+  y = 780
```

### Mandatory Layout Rules That Prevent Real-World Overlaps
1. **Headline Apex Clamp:** Enforce inside `MascotStageActor`: if `hasHeadline !== false`, clamp vertical jump lift so `computedY - currentLift - size - (speech ? 46 : 0) >= 178`.
2. **Outer-Edge Rope Attachment:** Whenever pulling drawers, shields, or pedestals (`edge_tug_slide`), attach `ropeToX`/`ropeToY` strictly to an outer handle tab or outer rim (`x <= targetLeft + 6` when pulling left; `x >= targetRight - 6` when pulling right) — **never** across card copy, checkmarks, or human faces.
3. **Dual-Label Bar Spacing:** Every progress bar / comparison row with left + right labels MUST use `display: flex; justify-content: space-between; align-items: center; gap: 24px; width: 100%` (prevents `Commitment` colliding with `24 Hours`). Status badges (`FINISH • 24h`) sit *below* or *after* the bar—never atop the title!
4. **Conditional Exclusion Badges (`WorldMap2D`):** Geographic exclusion callouts (e.g., excluding a country/region) MUST default to `excludeChina = false` and ONLY activate on the specific scene explaining that policy.
5. **No Top Chrome & Sleek Captions:** Zero top watermark pills or `01 / 80` scene counters. Display captions inside a single floating translucent pill centered at `bottom: 22px` with highlighted spoken words and a `3px` progress hairline underneath.

---

## 2. Curated Color Theme Presets (And Custom Theme Contract)

Every theme defines a single **unified seamless canvas** (`radial-gradient` from center to subtle vignette—never harsh vertical two-tone split backgrounds):

| Token | Warm Editorial Cream *(Default)* | Midnight Constellation | Botanical Sage Studio | Crisp Swiss Minimalist |
| :--- | :--- | :--- | :--- | :--- |
| `bg` / `bgVignette` | `#F5EFE6` → `#EAE0D2` | `#0E111B` → `#07090F` | `#F3F5F0` → `#E3E8DF` | `#F8F7F4` → `#EAE8E1` |
| `card` | `#FBF7F0` | `#161B2B` | `#FAFBF8` | `#FFFFFF` |
| `ink` / `inkMuted` | `#1C1917` / `#5C534A` | `#F4EFE6` / `#A7AFC4` | `#17261E` / `#4E6156` | `#141413` / `#5A5852` |
| `terracotta` *(Primary Accent)* | `#C97A54` | `#E5A95C` *(Amber Gold)* | `#C66D51` | `#2B5B84` *(Swiss Blue)* |
| `plum` / `plumDeep` *(Brand)* | `#7C5CBF` / `#3B1848` | `#9C7CF4` / `#E9DFFE` | `#5F7A61` / `#263B2B` | `#D18B3B` / `#141413` |
| `sage` *(Success)* | `#3E7B5E` | `#53B488` | `#3D7A5A` | `#2E7D5B` |
| `rust` *(Alert)* | `#B8432E` | `#E06354` | `#B84A39` | `#C84031` |

When the user supplies custom brand colors, map them cleanly to this exact `THEME` object shape in `src/theme.ts` so every scene, pedestal, caption pill, and figure updates uniformly.

---

## 3. Logo Blending & Optical Pedestals

- **Seamless Light-Canvas Logo Blending:** If the user uploads a black/colored logo on white background for a light theme (`Warm Editorial Cream`, `Botanical Sage`, `Crisp Swiss`), apply `mixBlendMode: "multiply"` directly on Remotion's `<Img>` element so white pixels vanish effortlessly into `#F5EFE6` (avoid placing `opacity` / `transform` on a parent wrapper around `mixBlendMode`, which breaks isolation in Chromium!). For dark themes (`Midnight Constellation`), require a transparent PNG/SVG or invert monochrome light inks cleanly.
- **Optical Brand Pedestals (`BrandPedestal`):** Never paste tiny third-party icons onto corners of phone frames. Render all external logos centered inside spacious circular/squircle pedestals (`76–104px` container, `2px` border, soft 2D ground shadow, crisp bottom label, `>= 24px` spacing).

---

## 4. Filmic 2D Motion & Dynamic Atmospheres

- **Camera Clamp (`<= 1.03×`):** Apply smooth `Easing.bezier(0.22, 1, 0.36, 1)` motion to the `1560 × 780` stage (`zoomIn: 1.00→1.03`, `zoomOut: 1.03→1.00`, `panRight/Left: scale 1.015, tx ±16px`).
- **Chapter-Distinct Atmospheres (`CHAPTER_SKIES[1..N]`):** Vary cloud count, positions, drift speed, diagonal ivory light beams (`opacity: 0.08–0.12`), twinkling 4-point brand stars, and subtle foreground dust bokeh (`1.3×` parallax strictly outside Band B card text) per chapter so no two chapters look identical.
