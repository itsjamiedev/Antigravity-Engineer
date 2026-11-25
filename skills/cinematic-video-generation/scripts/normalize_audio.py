"""
Normalize human-recorded voiceover chapter files to broadcast streaming levels
(-16 LUFS, -1.5 dBTP, 48 kHz stereo MP3) and generate a Remotion duration manifest.

Requires ffmpeg & ffprobe on PATH. Zero pip installs required.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus"}


def natural_key(path: Path) -> list[Any]:
    parts = re.split(r"(\d+)", path.stem.lower())
    return [int(p) if p.isdigit() else p for p in parts]


def loudnorm_to_mp3(src_path: Path, dst_path: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(src_path),
        "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(dst_path),
    ]
    subprocess.run(cmd, check=True)


def probe_duration(path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    return float(out)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Normalize dropped human voiceover clips (-16 LUFS / 48 kHz) and output Remotion frame timings."
    )
    p.add_argument(
        "--input-dir",
        required=True,
        type=Path,
        help="Directory containing raw human voiceover files (.mp3/.wav/.m4a/etc.).",
    )
    p.add_argument(
        "--out-dir",
        default=Path("public/audio"),
        type=Path,
        help="Output folder for normalized part01.mp3..partNN.mp3 (default: public/audio).",
    )
    p.add_argument(
        "--prefix",
        default="part",
        help="Output filename prefix (default: part -> part01.mp3).",
    )
    p.add_argument(
        "--fps",
        default=30,
        type=int,
        help="Remotion FPS for frame calculations (default: 30).",
    )
    p.add_argument(
        "--skip-loudnorm",
        action="store_true",
        help="Copy/remux without applying ffmpeg loudnorm filter.",
    )
    p.add_argument(
        "--manifest",
        default=None,
        type=Path,
        help="Output manifest path (default: <out-dir>/chapter_durations.json).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input_dir.is_dir():
        print(f"Error: input directory does not exist: {args.input_dir}", file=sys.stderr)
        return 1

    files = sorted(
        (p for p in args.input_dir.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXTS),
        key=natural_key,
    )
    if not files:
        print(f"Error: no supported audio files found in {args.input_dir}", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    total_frames = 0

    for idx, src in enumerate(files, start=1):
        out_name = f"{args.prefix}{idx:02d}.mp3"
        dst = args.out_dir / out_name
        print(f"[{idx}/{len(files)}] {src.name} -> {out_name}")

        if args.skip_loudnorm and src.suffix.lower() == ".mp3":
            shutil.copy2(src, dst)
        else:
            loudnorm_to_mp3(src, dst)

        dur = probe_duration(dst)
        frames = math.ceil(dur * args.fps)
        total_frames += frames
        rows.append(
            {
                "chapter": idx,
                "sourceFile": src.name,
                "audioFile": f"audio/{out_name}",
                "durationSec": round(dur, 6),
                "durationInFrames": frames,
            }
        )
        print(f"    {dur:.3f}s -> {frames} frames (@ {args.fps} fps)")

    manifest_path = args.manifest or (args.out_dir / "chapter_durations.json")
    manifest_path.write_text(
        json.dumps(
            {
                "fps": args.fps,
                "totalFrames": total_frames,
                "totalSeconds": round(total_frames / args.fps, 3),
                "chapters": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nNormalized {len(rows)} chapter clips ({total_frames} total frames) -> {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
