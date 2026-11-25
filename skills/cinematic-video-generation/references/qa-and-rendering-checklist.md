# QA Verification, Multi-Agent Swarm & Master Rendering Checklist

---

## 1. Large Project Multi-Agent Swarm Architecture (`>= 30 scenes`)

When building 30–80+ scenes, split work into **strictly disjoint files** so parallel workers never collide:

| Swarm Role | Owned Files Only | Responsibilities |
| :--- | :--- | :--- |
| `stage-core` | `theme.ts`, `CinematicStage.tsx`, `DrawEngine.tsx`, `ForevernotedPitch.tsx`, `SceneRouter.tsx`, `public/sfx/*` | Dynamic chapter skies, camera bezier easing, multi-beat `sfxCues`, 12 WAVs + `ambient_bed.mp3`. |
| `mascot-cast` | `Mascot.tsx` *(if Mascot=Yes)*, `HumanCast.tsx`, `BrandPedestal.tsx`, `Icons.tsx` | 16 expressions × 16 motions, Headline Apex Guard, Human figures, `WorldMap2D`, optical pedestals. |
| `scenes-a/b/c` | `ScenesPartA.tsx`, `ScenesPartB.tsx`, `ScenesPartC.tsx` | Sharded by chapter range (~25–30 scenes each), obeying the 4-Band Grid + zero-repeat table. |
| `qa-verifier` | *Zero source files (read/run/inspect only)* | Gate 1 TypeScript + automated audit, Gate 2 multi-still inspection via `read_file`, Gate 3 `CRF 14` render + `ffprobe`. |

*(Always check active model quotas/availability before pinning swarm models; keep workspace `inherit` unless running in a git-branchable repo.)*

---

## 2. Gate 1 — Automated Compile & Consistency Audit

Before rendering ANY video or PNG:
1. Run TypeScript check inside `<project-dir>`:
   ```bash
   npx tsc --noEmit
   ```
   Must exit `0`.
2. Run [../scripts/audit_video_project.py](../scripts/audit_video_project.py):
   ```bash
   python scripts/audit_video_project.py --project-dir <remotion-project-dir>
   ```
   Verifies automatically:
   - All 12 studio WAV SFX + `ambient_bed.mp3` exist (`>0` bytes).
   - Zero UTF-8 mojibake (`â€`, `Ã—`, `â†`, `âœ`) across all `.tsx` files.
   - Zero `splitSand` remnants (unless user requested split backgrounds).
   - Every scene specifies an active `expression` and `motion` *(if Mascot = Yes)* with **0 consecutive repeats (`i → i+1`)**.
   - Prints exact midpoint global frame numbers computed from `src/data/chapters.ts` for Gate 2 still rendering.

---

## 3. Gate 2 — Mandatory Multi-Still Visual QA Inspection

**NEVER run a multi-minute MP4 render blind.** First render **6–14 representative midpoint PNG stills** covering opening/closing, widest horizontal diagrams, dual-label comparison bars, scrolling text documents, world maps, and mascot pulls/hops:

```bash
npx remotion still src/index.ts <CompositionId> qa_stills/scene01.png --frame=<MIDPOINT>
```

Visually inspect **EVERY single PNG still** (`read_file`) against this 10-point inspection checklist:
1. **Zero Band A Overlap:** Headlines & kickers have complete breathing room; no mascot head, speech pill, or jump apex touches text.
2. **Zero Card/Text Occlusion:** No pull ropes cross drawer copy, bullet lists, checkmarks, or human faces.
3. **Dual-Label Spacing:** Left and right header labels on bars (`Title` vs `24 Hours ✓`) have crisp horizontal whitespace; inline badges sit clear of text.
4. **Zero Canvas Clipping:** All margins comfortably inside `1920 × 1080` (`SAFE_W = 1560`, `SAFE_H = 780`, camera `<= 1.03×`).
5. **Logo Integration:** Uploaded logo blends cleanly (`mixBlendMode: "multiply"` or transparent alpha—zero ugly white/black rectangle).
6. **Optical Pedestals:** Third-party SVGs sit centered inside spacious pedestals—never pasted awkwardly onto phone corners.
7. **Geographic Accuracy:** Map exclusions (`excludeChina`, etc.) only appear on the exact scene that discusses them.
8. **Diverse Friendly Expressions:** Mascot shows warm, charming expressions matched to each beat—no repetitive harsh grumpy pull faces.
9. **Chapter Sky Variety:** Background clouds, light beams, and subtle dust motes vary smoothly across chapters.
10. **Clean Caption Legibility:** No top chrome; bottom caption bar sits cleanly without colliding with Band C characters.

If ANY single item fails, fix the owning file cleanly, re-render the affected still(s), and re-inspect via `read_file` BEFORE Gate 3.

---

## 4. Gate 3 — Master `CRF 14` Encoding & `ffprobe` Verification

Once 100% of inspected stills pass:
```bash
npx remotion render src/index.ts <CompositionId> ../Master_Cinematic.mp4 \
  --codec=h264 --crf=14 --pixel-format=yuv420p \
  --audio-codec=aac --audio-bitrate=192k --concurrency=4
```

Verify final file integrity immediately:
```bash
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_name,width,height,r_frame_rate,bit_rate \
  -of default=noprint_wrappers=1 ../Master_Cinematic.mp4
```
Confirm:
- `width=1920`, `height=1080`, `r_frame_rate=30/1`, `codec_name=h264`
- Audio `codec_name=aac` (`~192k`)
- Output duration matches `TOTAL_FRAMES / 30` (`±0.3s` container padding) and file size `> 0`.
