"""
Generate chapter voiceover audio using the Fish Audio (Fish Speech) TTS API.

Endpoint: POST https://api.fish.audio/v1/tts
Auth:     FISH_API_KEY environment variable (or --api-key CLI flag)

No external pip dependencies required (uses Python stdlib + optional ffmpeg/ffprobe).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_URL = "https://api.fish.audio/v1/tts"
SUPPORTED_MODELS = ("s2.1-pro", "s2.1-pro-free", "s2-pro", "s3-pro", "drama-3")
SUPPORTED_FORMATS = ("mp3", "wav", "pcm", "opus")


def synthesize_tts(
    *,
    text: str,
    api_key: str,
    model: str = "s2.1-pro",
    reference_id: str | None = None,
    audio_format: str = "mp3",
    speed: float = 1.0,
    normalize_text: bool = True,
    timeout: int = 120,
) -> bytes:
    """Call POST https://api.fish.audio/v1/tts and return raw audio bytes."""
    payload: dict[str, Any] = {
        "text": text,
        "format": audio_format,
        "normalize": normalize_text,
        "speed": speed,
    }
    if reference_id:
        payload["reference_id"] = reference_id

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "model": model,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Fish Audio API HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Fish Audio API network error: {exc.reason}") from exc


def loudnorm_mp3(src_path: Path, dst_path: Path) -> None:
    """Normalize audio to EBU R128 (-16 LUFS, -1.5 dBTP, 48 kHz) via ffmpeg."""
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
    """Return duration in seconds via ffprobe."""
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


def load_chapters(script_path: Path) -> list[dict[str, Any]]:
    raw = json.loads(script_path.read_text(encoding="utf-8-sig"))
    if isinstance(raw, dict) and "chapters" in raw:
        chapters = raw["chapters"]
    elif isinstance(raw, list):
        chapters = raw
    else:
        raise ValueError("Script JSON must be a list of chapters or {\"chapters\": [...]}.")

    normalized: list[dict[str, Any]] = []
    for idx, ch in enumerate(chapters, start=1):
        ch_num = int(ch.get("chapter", idx))
        text = str(ch.get("text", "")).strip()
        if not text:
            raise ValueError(f"Chapter {ch_num} is missing non-empty 'text'.")
        normalized.append(
            {
                "chapter": ch_num,
                "text": text,
                "reference_id": ch.get("reference_id"),
                "scenes": ch.get("scenes", []),
            }
        )
    return normalized


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Synthesize per-chapter voiceovers via Fish Speech / Fish Audio TTS API."
    )
    p.add_argument(
        "--script",
        required=True,
        type=Path,
        help="Path to chapters_script.json containing chapter texts and optional scene metadata.",
    )
    p.add_argument(
        "--out-dir",
        default=Path("public/audio"),
        type=Path,
        help="Destination folder for part01.mp3..partNN.mp3 (default: public/audio).",
    )
    p.add_argument(
        "--model",
        default="s2.1-pro",
        choices=SUPPORTED_MODELS,
        help="Fish Audio `model` header (default: s2.1-pro).",
    )
    p.add_argument(
        "--reference-id",
        default=None,
        help="Voice model UUID (`reference_id`). Leave unset for model default voice.",
    )
    p.add_argument(
        "--format",
        default="mp3",
        choices=SUPPORTED_FORMATS,
        help="Requested API output format before normalization (default: mp3).",
    )
    p.add_argument(
        "--speed",
        default=1.0,
        type=float,
        help="Speaking speed multiplier 0.5..2.0 (default: 1.0).",
    )
    p.add_argument(
        "--api-key",
        default=None,
        help="Fish Audio API key (defaults to FISH_API_KEY environment variable).",
    )
    p.add_argument(
        "--fps",
        default=30,
        type=int,
        help="Remotion composition FPS for durationInFrames calculation (default: 30).",
    )
    p.add_argument(
        "--no-loudnorm",
        action="store_true",
        help="Skip ffmpeg -16 LUFS normalization and save raw API output directly.",
    )
    p.add_argument(
        "--manifest",
        default=None,
        type=Path,
        help="Path to write chapter_durations.json (default: <out-dir>/chapter_durations.json).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate script JSON and print planned API requests without calling the API.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not (0.5 <= args.speed <= 2.0):
        print("Error: --speed must be between 0.5 and 2.0", file=sys.stderr)
        return 2

    chapters = load_chapters(args.script)
    if args.dry_run:
        for ch in chapters:
            ref = ch["reference_id"] or args.reference_id or "<default>"
            print(
                f"[dry-run] Chapter {ch['chapter']:02d}: model={args.model} ref={ref} "
                f"speed={args.speed} chars={len(ch['text'])}"
            )
        return 0

    api_key = args.api_key or os.environ.get("FISH_API_KEY", "").strip()
    if not api_key:
        print(
            "Error: Missing Fish Audio API key. Set FISH_API_KEY environment variable or pass --api-key.",
            file=sys.stderr,
        )
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, Any]] = []
    total_frames = 0

    for ch in chapters:
        num = ch["chapter"]
        ref_id = ch["reference_id"] or args.reference_id
        raw_name = f"_raw_part{num:02d}.{args.format}"
        final_ext = args.format if args.no_loudnorm else "mp3"
        final_name = f"part{num:02d}.{final_ext}"
        raw_path = args.out_dir / raw_name
        final_path = args.out_dir / final_name

        print(f"Synthesizing Chapter {num:02d} -> {final_name} (model={args.model})...")
        audio_bytes = synthesize_tts(
            text=ch["text"],
            api_key=api_key,
            model=args.model,
            reference_id=ref_id,
            audio_format=args.format,
            speed=args.speed,
        )
        raw_path.write_bytes(audio_bytes)

        if args.no_loudnorm:
            raw_path.replace(final_path)
        else:
            loudnorm_mp3(raw_path, final_path)
            raw_path.unlink(missing_ok=True)

        duration_sec = probe_duration(final_path)
        frames = math.ceil(duration_sec * args.fps)
        total_frames += frames
        manifest_rows.append(
            {
                "chapter": num,
                "audioFile": f"audio/{final_name}",
                "durationSec": round(duration_sec, 6),
                "durationInFrames": frames,
                "scenes": ch["scenes"],
            }
        )
        print(f"  Saved {final_path} ({duration_sec:.2f}s / {frames} frames)")

    manifest_path = args.manifest or (args.out_dir / "chapter_durations.json")
    manifest_path.write_text(
        json.dumps(
            {
                "fps": args.fps,
                "totalFrames": total_frames,
                "totalSeconds": round(total_frames / args.fps, 3),
                "chapters": manifest_rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nDone! Wrote {len(manifest_rows)} chapters ({total_frames} frames) -> {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
