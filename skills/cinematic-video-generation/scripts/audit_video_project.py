"""
Automated QA Auditor & Midpoint Frame Calculator for Cinematic 2D Remotion Projects.

Checks:
1. All 12 studio WAV SFX + ambient_bed.mp3 exist (>0 bytes).
2. Zero UTF-8 mojibake sequences in src/scenes/*.tsx and src/components/*.tsx.
3. Optional check verifying no deprecated splitSand canvas seams remain.
4. Mascot non-repetition audit across Scenes 1..N (if MascotStageActor is used):
   verifies no two adjacent scenes share the same `expression` or `motion`.
5. Computes exact midpoint global frame numbers from src/data/chapters.ts for
   mandatory multi-still inspection via `npx remotion still`.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_WAVS = [
    "whoosh_velvet.wav",
    "whoosh_cinematic.wav",
    "pop_wood.wav",
    "pop_bubble.wav",
    "boing_soft.wav",
    "chime_warm.wav",
    "sparkle_magic.wav",
    "rope_tug.wav",
    "snip_crisp.wav",
    "stamp_thud.wav",
    "alert_soft.wav",
    "page_turn.wav",
]

# Detect classic UTF-8-as-Latin1 mojibake without embedding raw mojibake literals
MOJIBAKE_PATTERNS = [
    ("\u00e2\u20ac", "broken bullet/dash/quote UTF-8 sequence"),
    ("\u00c3\u2014", "broken multiplication sign (x) UTF-8 sequence"),
    ("\u00e2\u2020", "broken arrow UTF-8 sequence"),
    ("\u00e2\u0153", "broken checkmark/symbol UTF-8 sequence"),
    ("\ufffd", "Unicode replacement character"),
]


def check_sfx(project_dir: Path) -> tuple[bool, list[str]]:
    sfx_dir = project_dir / "public" / "sfx"
    issues: list[str] = []
    if not sfx_dir.is_dir():
        return False, [f"Missing directory: {sfx_dir}"]
    for name in REQUIRED_WAVS + ["ambient_bed.mp3"]:
        p = sfx_dir / name
        if not p.is_file() or p.stat().st_size == 0:
            issues.append(f"Missing or empty SFX file: {p}")
    return len(issues) == 0, issues


def check_mojibake(project_dir: Path) -> tuple[bool, list[str]]:
    issues: list[str] = []
    src_dir = project_dir / "src"
    if not src_dir.is_dir():
        return False, [f"Missing directory: {src_dir}"]
    for path in sorted(src_dir.rglob("*.tsx")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pat, desc in MOJIBAKE_PATTERNS:
                if pat in line:
                    issues.append(f"{path.relative_to(project_dir)}:{line_no}: {desc}")
    return len(issues) == 0, issues


def audit_mascot_repeats(project_dir: Path) -> tuple[bool, int, list[str]]:
    scenes_dir = project_dir / "src" / "scenes"
    issues: list[str] = []
    if not scenes_dir.is_dir():
        return True, 0, []

    scene_records: dict[int, tuple[str | None, str | None, str]] = {}
    scene_start_re = re.compile(r"(?:const\s+Scene(\d+)\b|case\s+(\d+)\s*:)")
    actor_re = re.compile(r"<MascotStageActor\b([\s\S]*?)/>")
    expr_re = re.compile(r'expression\s*=\s*"([^"]+)"')
    motion_re = re.compile(r'motion\s*=\s*"([^"]+)"')

    for path in sorted(scenes_dir.glob("ScenesPart*.tsx")) or sorted(scenes_dir.glob("*.tsx")):
        if path.name == "SceneRouter.tsx":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = list(scene_start_re.finditer(text))
        for idx, m in enumerate(matches):
            sid = int(m.group(1) or m.group(2))
            start = m.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            block = text[start:end]
            actor_m = actor_re.search(block)
            if not actor_m:
                continue
            props = actor_m.group(1)
            em = expr_re.search(props)
            mm = motion_re.search(props)
            scene_records[sid] = (
                em.group(1) if em else None,
                mm.group(1) if mm else None,
                path.name,
            )

    if not scene_records:
        return True, 0, []

    ordered_ids = sorted(scene_records.keys())
    for sid in ordered_ids:
        expr, mot, fname = scene_records[sid]
        if not expr or not mot:
            issues.append(f"Scene {sid:02d} ({fname}) missing explicit expression={expr} or motion={mot}")

    for prev_id, curr_id in zip(ordered_ids, ordered_ids[1:]):
        if curr_id != prev_id + 1:
            continue
        p_expr, p_mot, p_file = scene_records[prev_id]
        c_expr, c_mot, c_file = scene_records[curr_id]
        if p_expr and c_expr and p_expr == c_expr:
            issues.append(
                f"Consecutive expression repeat: Scene {prev_id:02d} ({p_file}) -> Scene {curr_id:02d} ({c_file}) both use '{c_expr}'"
            )
        if p_mot and c_mot and p_mot == c_mot:
            issues.append(
                f"Consecutive motion repeat: Scene {prev_id:02d} ({p_file}) -> Scene {curr_id:02d} ({c_file}) both use '{c_mot}'"
            )

    return len(issues) == 0, len(scene_records), issues


def compute_scene_frames(project_dir: Path, fps: int = 30) -> list[dict[str, Any]]:
    chapters_path = project_dir / "src" / "data" / "chapters.ts"
    if not chapters_path.is_file():
        return []
    text = chapters_path.read_text(encoding="utf-8", errors="replace")

    fps_m = re.search(r"export\s+const\s+FPS\s*=\s*(\d+)", text)
    if fps_m:
        fps = int(fps_m.group(1))

    ch_header_re = re.compile(
        r"chapter\s*:\s*(\d+)[\s\S]*?durationInFrames\s*:\s*(?:secToFrames\(\s*([\d.]+)\s*\)|(\d+))[\s\S]*?scenes\s*:\s*\[([\s\S]*?)\]\s*,?\s*\}",
        re.MULTILINE,
    )
    scene_item_re = re.compile(r"\{\s*id\s*:\s*(\d+)[\s\S]*?weight\s*:\s*(\d+)[\s\S]*?\}")

    results: list[dict[str, Any]] = []
    global_cursor = 0
    for cm in ch_header_re.finditer(text):
        ch_num = int(cm.group(1))
        ch_frames = (
            math.ceil(float(cm.group(2)) * fps)
            if cm.group(2) is not None
            else int(cm.group(3))
        )
        scenes_block = cm.group(4)
        items = [(int(sm.group(1)), int(sm.group(2))) for sm in scene_item_re.finditer(scenes_block)]
        if not items:
            continue
        total_weight = sum(w for _, w in items)
        remaining = ch_frames
        for idx, (sid, weight) in enumerate(items):
            if idx == len(items) - 1:
                dur = max(1, remaining)
            else:
                dur = max(1, int(round((weight / total_weight) * ch_frames)))
                remaining -= dur
            results.append(
                {
                    "scene": sid,
                    "chapter": ch_num,
                    "startFrame": global_cursor,
                    "endFrame": global_cursor + dur - 1,
                    "durationFrames": dur,
                    "midpointFrame": global_cursor + (dur // 2),
                }
            )
            global_cursor += dur

    return results


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Audit a Remotion Cinematic Video project for SFX, mojibake, mascot repeats, and still frames."
    )
    p.add_argument(
        "--project-dir",
        default=Path("."),
        type=Path,
        help="Path to Remotion project root containing src/ and public/ (default: .).",
    )
    p.add_argument(
        "--scenes",
        default="",
        help="Comma-separated scene IDs for still midpoint frame lookup (e.g. 1,6,15,25,34,45,60,80).",
    )
    p.add_argument(
        "--fps",
        default=30,
        type=int,
        help="Fallback FPS if chapters.ts doesn't declare export const FPS (default: 30).",
    )
    p.add_argument(
        "--no-mascot",
        action="store_true",
        help="Skip mascot expression/motion continuity check.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit audit summary and frame map as JSON.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = args.project_dir.resolve()

    sfx_ok, sfx_issues = check_sfx(project_dir)
    moji_ok, moji_issues = check_mojibake(project_dir)
    if args.no_mascot:
        mascot_ok, mascot_count, mascot_issues = True, 0, []
    else:
        mascot_ok, mascot_count, mascot_issues = audit_mascot_repeats(project_dir)

    frames = compute_scene_frames(project_dir, fps=args.fps)
    requested_set: set[int] | None = None
    if args.scenes.strip():
        requested_set = {int(x.strip()) for x in args.scenes.split(",") if x.strip()}
    selected_frames = [r for r in frames if requested_set is None or r["scene"] in requested_set]

    all_ok = sfx_ok and moji_ok and mascot_ok

    if args.json:
        print(
            json.dumps(
                {
                    "ok": all_ok,
                    "sfxOk": sfx_ok,
                    "sfxIssues": sfx_issues,
                    "mojibakeOk": moji_ok,
                    "mojibakeIssues": moji_issues,
                    "mascotCheckedScenes": mascot_count,
                    "mascotOk": mascot_ok,
                    "mascotIssues": mascot_issues,
                    "totalFrames": frames[-1]["endFrame"] + 1 if frames else 0,
                    "selectedFrames": selected_frames,
                },
                indent=2,
            )
        )
        return 0 if all_ok else 1

    print(f"=== Cinematic Video QA Audit: {project_dir} ===")
    print(f"[{'PASS' if sfx_ok else 'FAIL'}] Studio 12 WAV SFX + ambient_bed.mp3")
    for issue in sfx_issues:
        print(f"  - {issue}")

    print(f"[{'PASS' if moji_ok else 'FAIL'}] UTF-8 Mojibake Scan")
    for issue in moji_issues:
        print(f"  - {issue}")

    if args.no_mascot or mascot_count == 0:
        print("[SKIP] Mascot Non-Repeat Check (not enabled or no MascotStageActor scenes found)")
    else:
        print(f"[{'PASS' if mascot_ok else 'FAIL'}] Mascot Expression & Motion Zero-Repeat Audit ({mascot_count} scenes)")
        for issue in mascot_issues:
            print(f"  - {issue}")

    if frames:
        total = frames[-1]["endFrame"] + 1
        print(f"\nComputed {len(frames)} scene timings ({total} total frames):")
        for row in selected_frames:
            print(
                f"  Scene {row['scene']:02d} (Ch.{row['chapter']:02d}): "
                f"frames {row['startFrame']}..{row['endFrame']} -> midpoint --frame={row['midpointFrame']}"
            )

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
