"""
Cinematic 2D Studio SFX & Ambient Bed Synthesizer.
Generates 12 warm, organic, non-harsh studio WAV SFX + a seamlessly loopable
45-second felt-piano/pad ambient_bed.mp3 in a target directory (default: ./public/sfx).

Zero external pip dependencies required (stdlib + ffmpeg for ambient_bed.mp3).
"""

from __future__ import annotations

import argparse
import math
import os
import random
import struct
import subprocess
import wave
from pathlib import Path

SR = 44100


def clamp(v: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return lo if v < lo else (hi if v > hi else v)


def write_wav_mono(out_dir: Path, filename: str, samples: list[float], peak: float = 0.85) -> Path:
    path = out_dir / filename
    mx = max((abs(x) for x in samples), default=1.0)
    scale = (peak / mx) if mx > 1e-6 else 1.0
    fade = min(int(0.002 * SR), len(samples) // 4)
    buf = bytearray(len(samples) * 2)
    for i, s in enumerate(samples):
        g = 1.0
        if fade > 0:
            if i < fade:
                g = i / fade
            elif i >= len(samples) - fade:
                g = (len(samples) - 1 - i) / fade
        val = int(clamp(s * scale * g, -0.99, 0.99) * 32767)
        struct.pack_into("<h", buf, i * 2, val)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(buf)
    return path


def write_wav_stereo(
    out_dir: Path,
    filename: str,
    left: list[float],
    right: list[float],
    peak: float = 0.85,
    fade_edges: bool = True,
) -> Path:
    path = out_dir / filename
    n = min(len(left), len(right))
    mx = max(max((abs(x) for x in left[:n]), default=1.0), max((abs(x) for x in right[:n]), default=1.0))
    scale = (peak / mx) if mx > 1e-6 else 1.0
    fade = min(int(0.003 * SR), n // 4) if fade_edges else 0
    buf = bytearray(n * 4)
    for i in range(n):
        g = 1.0
        if fade > 0:
            if i < fade:
                g = i / fade
            elif i >= n - fade:
                g = (n - 1 - i) / fade
        lv = int(clamp(left[i] * scale * g, -0.99, 0.99) * 32767)
        rv = int(clamp(right[i] * scale * g, -0.99, 0.99) * 32767)
        struct.pack_into("<hh", buf, i * 4, lv, rv)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(buf)
    return path


def lp_step(prev: float, inp: float, cutoff_hz: float) -> float:
    rc = 1.0 / (2.0 * math.pi * max(20.0, cutoff_hz))
    dt = 1.0 / SR
    alpha = dt / (rc + dt)
    return prev + alpha * (inp - prev)


def gen_whoosh_velvet(out_dir: Path) -> None:
    dur = 0.42
    n = int(dur * SR)
    rng = random.Random(101)
    out = [0.0] * n
    lp1 = lp2 = phase = 0.0
    for i in range(n):
        u = i / n
        env = math.sin(math.pi * u) ** 1.6
        cutoff = 200.0 + 780.0 * (math.sin(math.pi * u) ** 1.3)
        noise = rng.uniform(-1.0, 1.0)
        lp1 = lp_step(lp1, noise, cutoff)
        lp2 = lp_step(lp2, lp1, cutoff * 0.9)
        freq = 135.0 + 85.0 * math.sin(math.pi * u)
        phase += 2.0 * math.pi * freq / SR
        out[i] = env * (lp2 * 2.2 + 0.14 * math.sin(phase))
    write_wav_mono(out_dir, "whoosh_velvet.wav", out, peak=0.72)


def gen_whoosh_cinematic(out_dir: Path) -> None:
    dur = 0.62
    n = int(dur * SR)
    rng = random.Random(202)
    left = [0.0] * n
    right = [0.0] * n
    lp1_l = lp2_l = lp1_r = lp2_r = ph_l = ph_r = 0.0
    for i in range(n):
        u = i / n
        env = (math.sin(math.pi * u) ** 1.45) * (1.0 - 0.15 * u)
        cutoff = 150.0 + 1050.0 * (math.sin(math.pi * u) ** 1.2)
        lp1_l = lp_step(lp1_l, rng.uniform(-1.0, 1.0), cutoff)
        lp2_l = lp_step(lp2_l, lp1_l, cutoff * 0.85)
        lp1_r = lp_step(lp1_r, rng.uniform(-1.0, 1.0), cutoff * 1.05)
        lp2_r = lp_step(lp2_r, lp1_r, cutoff * 0.88)
        f = 95.0 + 90.0 * math.sin(math.pi * u)
        ph_l += 2.0 * math.pi * f / SR
        ph_r += 2.0 * math.pi * (f * 1.008) / SR
        pan_l = math.cos(u * math.pi * 0.5) * 0.75 + 0.35
        pan_r = math.sin(u * math.pi * 0.5) * 0.75 + 0.35
        left[i] = env * pan_l * (lp2_l * 2.3 + 0.18 * math.sin(ph_l))
        right[i] = env * pan_r * (lp2_r * 2.3 + 0.18 * math.sin(ph_r))
    write_wav_stereo(out_dir, "whoosh_cinematic.wav", left, right, peak=0.76)


def gen_pop_wood(out_dir: Path) -> None:
    dur = 0.17
    n = int(dur * SR)
    rng = random.Random(303)
    out = [0.0] * n
    ph1 = ph2 = lp = 0.0
    for i in range(n):
        t = i / SR
        env_atk = min(1.0, t / 0.004)
        env1 = env_atk * math.exp(-t * 28.0)
        env2 = env_atk * math.exp(-t * 68.0)
        f = 285.0 + 240.0 * math.exp(-t * 85.0)
        ph1 += 2.0 * math.pi * f / SR
        ph2 += 2.0 * math.pi * (f * 2.76) / SR
        mallet = lp_step(lp, rng.uniform(-1.0, 1.0), 1200.0) * math.exp(-t * 220.0)
        lp = mallet
        out[i] = env1 * math.sin(ph1) + 0.24 * env2 * math.sin(ph2) + 0.18 * mallet
    write_wav_mono(out_dir, "pop_wood.wav", out, peak=0.80)


def gen_pop_bubble(out_dir: Path) -> None:
    dur = 0.19
    n = int(dur * SR)
    out = [0.0] * n
    ph = 0.0
    for i in range(n):
        t = i / SR
        env = min(1.0, t / 0.008) * math.exp(-t * 22.0)
        f = 350.0 + 420.0 * (1.0 - math.exp(-t * 26.0))
        ph += 2.0 * math.pi * f / SR
        out[i] = env * (math.sin(ph) + 0.15 * math.sin(2.0 * ph))
    write_wav_mono(out_dir, "pop_bubble.wav", out, peak=0.76)


def gen_boing_soft(out_dir: Path) -> None:
    dur = 0.36
    n = int(dur * SR)
    out = [0.0] * n
    ph = 0.0
    for i in range(n):
        t = i / SR
        env = min(1.0, t / 0.010) * math.exp(-t * 7.8)
        glide = 215.0 + 235.0 * (1.0 - math.exp(-t * 16.0))
        wobble = 26.0 * math.sin(2.0 * math.pi * 17.5 * t) * math.exp(-t * 7.0)
        ph += 2.0 * math.pi * (glide + wobble) / SR
        out[i] = env * (math.sin(ph) + 0.20 * math.sin(2.0 * ph) * math.exp(-t * 10.0))
    write_wav_mono(out_dir, "boing_soft.wav", out, peak=0.78)


def gen_chime_warm(out_dir: Path) -> None:
    dur = 0.90
    n = int(dur * SR)
    out = [0.0] * n
    notes = [523.25, 659.25, 783.99, 987.77, 1174.66]  # Cmaj9 harp/bell chord
    for idx, freq in enumerate(notes):
        start = int(idx * 0.026 * SR)
        amp = 0.45 * (0.92 ** idx)
        for i in range(start, n):
            t = (i - start) / SR
            env = min(1.0, t / 0.008) * math.exp(-t * (4.2 + idx * 0.35))
            s = (
                math.sin(2.0 * math.pi * freq * t)
                + 0.22 * math.sin(2.0 * math.pi * freq * 2.0 * t) * math.exp(-t * 6.0)
                + 0.08 * math.sin(2.0 * math.pi * freq * 3.0 * t) * math.exp(-t * 10.0)
            )
            out[i] += amp * env * s
    write_wav_mono(out_dir, "chime_warm.wav", out, peak=0.78)


def gen_sparkle_magic(out_dir: Path) -> None:
    dur = 0.72
    n = int(dur * SR)
    out = [0.0] * n
    notes = [1318.51, 1661.22, 1975.53, 2637.02]  # E6, G#6, B6, E7 shimmer
    for idx, freq in enumerate(notes):
        start = int(idx * 0.062 * SR)
        amp = 0.42 * (0.88 ** idx)
        for i in range(start, n):
            t = (i - start) / SR
            env = min(1.0, t / 0.006) * math.exp(-t * (6.8 + idx * 0.5))
            shimmer = 1.0 + 0.08 * math.sin(2.0 * math.pi * 12.0 * t)
            s = math.sin(2.0 * math.pi * freq * t) + 0.16 * math.sin(2.0 * math.pi * freq * 2.0 * t) * math.exp(-t * 12.0)
            out[i] += amp * env * shimmer * s
    write_wav_mono(out_dir, "sparkle_magic.wav", out, peak=0.70)


def gen_rope_tug(out_dir: Path) -> None:
    dur = 0.30
    n = int(dur * SR)
    rng = random.Random(404)
    out = [0.0] * n
    lp1 = lp2 = hp_prev = ph = 0.0
    for i in range(n):
        t = i / SR
        u = i / n
        pulse = 0.75 + 0.25 * math.sin(2.0 * math.pi * 24.0 * t)
        env = (math.sin(math.pi * u) ** 1.2) * pulse
        lp1 = lp_step(lp1, rng.uniform(-1.0, 1.0), 680.0)
        lp2 = lp_step(lp2, lp1, 520.0)
        hp = lp2 - lp_step(hp_prev, lp2, 190.0)
        hp_prev = lp2
        ph += 2.0 * math.pi * (130.0 + 75.0 * (u ** 0.8)) / SR
        out[i] = env * hp * 2.4 + 0.28 * math.sin(ph) * math.sin(math.pi * u)
    write_wav_mono(out_dir, "rope_tug.wav", out, peak=0.76)


def gen_snip_crisp(out_dir: Path) -> None:
    dur = 0.16
    n = int(dur * SR)
    rng = random.Random(505)
    out = [0.0] * n
    lp_hi = lp_lo = 0.0
    for i in range(n):
        t = i / SR
        lp_hi = lp_step(lp_hi, rng.uniform(-1.0, 1.0), 4600.0)
        lp_lo = lp_step(lp_lo, lp_hi, 1500.0)
        bp = lp_hi - lp_lo
        glide_env = math.exp(-((t - 0.022) / 0.015) ** 2) * 0.45
        snip_t = max(0.0, t - 0.038)
        snip_env = (min(1.0, snip_t / 0.002) * math.exp(-snip_t * 62.0)) if t >= 0.038 else 0.0
        steel = (
            math.sin(2.0 * math.pi * 2180.0 * snip_t) * 0.45
            + math.sin(2.0 * math.pi * 3640.0 * snip_t) * 0.25
        ) * math.exp(-snip_t * 75.0)
        out[i] = bp * (glide_env + snip_env * 1.4) + (steel * snip_env * 0.55 if t >= 0.038 else 0.0)
    write_wav_mono(out_dir, "snip_crisp.wav", out, peak=0.76)


def gen_stamp_thud(out_dir: Path) -> None:
    dur = 0.24
    n = int(dur * SR)
    rng = random.Random(606)
    out = [0.0] * n
    ph = lp = 0.0
    for i in range(n):
        t = i / SR
        env = min(1.0, t / 0.003) * math.exp(-t * 19.0)
        ph += 2.0 * math.pi * (56.0 + 105.0 * math.exp(-t * 48.0)) / SR
        lp = lp_step(lp, rng.uniform(-1.0, 1.0), 420.0)
        felt = lp * math.exp(-t * 42.0) * 1.6
        out[i] = env * (math.sin(ph) + 0.18 * math.sin(2.0 * ph)) + felt
    write_wav_mono(out_dir, "stamp_thud.wav", out, peak=0.84)


def gen_alert_soft(out_dir: Path) -> None:
    dur = 0.38
    n = int(dur * SR)
    out = [0.0] * n
    tones = [(0.0, 349.23, 0.72), (0.115, 293.66, 0.85)]
    for start_s, freq, amp in tones:
        start = int(start_s * SR)
        for i in range(start, n):
            t = (i - start) / SR
            env = min(1.0, t / 0.010) * math.exp(-t * 11.5)
            s = math.sin(2.0 * math.pi * freq * t) + 0.18 * math.sin(2.0 * math.pi * freq * 2.0 * t) * math.exp(-t * 18.0)
            out[i] += amp * env * s
    write_wav_mono(out_dir, "alert_soft.wav", out, peak=0.72)


def gen_page_turn(out_dir: Path) -> None:
    dur = 0.34
    n = int(dur * SR)
    rng = random.Random(707)
    out = [0.0] * n
    lp_hi = lp_lo = 0.0
    for i in range(n):
        t = i / SR
        lp_hi = lp_step(lp_hi, rng.uniform(-1.0, 1.0), 3100.0)
        lp_lo = lp_step(lp_lo, lp_hi, 820.0)
        bp = lp_hi - lp_lo
        w1 = math.exp(-((t - 0.09) / 0.055) ** 2)
        w2 = 0.78 * math.exp(-((t - 0.21) / 0.065) ** 2)
        out[i] = bp * (w1 + w2) * 1.9
    write_wav_mono(out_dir, "page_turn.wav", out, peak=0.68)


def gen_ambient_bed(out_dir: Path) -> None:
    """Smoothly loopable 45-second warm felt-piano & velvet pad ambient bed."""
    dur = 45.0
    n = int(dur * SR)
    left = [0.0] * n
    right = [0.0] * n
    bar_sec = dur / 8.0
    chords = [
        ([130.81, 196.00, 246.94, 293.66, 329.63], [261.63, 329.63, 392.00, 493.88, 587.33]),
        ([130.81, 196.00, 246.94, 329.63], [329.63, 392.00, 493.88, 523.25]),
        ([110.00, 164.81, 220.00, 246.94, 261.63], [220.00, 261.63, 329.63, 392.00, 493.88]),
        ([110.00, 164.81, 220.00, 261.63], [261.63, 329.63, 392.00, 440.00]),
        ([87.31, 174.61, 220.00, 261.63, 329.63], [174.61, 261.63, 329.63, 392.00, 440.00]),
        ([87.31, 174.61, 220.00, 261.63], [220.00, 261.63, 329.63, 349.23]),
        ([98.00, 196.00, 246.94, 293.66, 329.63], [196.00, 246.94, 293.66, 392.00, 440.00]),
        ([98.00, 146.83, 196.00, 261.63, 293.66], [196.00, 261.63, 293.66, 392.00]),
    ]

    for bar_idx, (pad_freqs, piano_notes) in enumerate(chords):
        bar_start_s = bar_idx * bar_sec
        pad_len_s = bar_sec + 1.8
        pad_samples = int(pad_len_s * SR)
        start_idx = int(bar_start_s * SR)

        for k in range(pad_samples):
            t = k / SR
            if t < 1.2:
                env = 0.5 - 0.5 * math.cos(math.pi * t / 1.2)
            elif t > pad_len_s - 1.8:
                rem = (pad_len_s - t) / 1.8
                env = 0.5 - 0.5 * math.cos(math.pi * max(0.0, rem))
            else:
                env = 1.0
            breath = 0.88 + 0.12 * math.sin(2.0 * math.pi * 0.22 * t)
            sl = sr = 0.0
            for fi, f in enumerate(pad_freqs):
                w = 0.15 if fi > 0 else 0.18
                det = 1.0 + (0.0018 if fi % 2 == 0 else -0.0018)
                sl += w * math.sin(2.0 * math.pi * f * t)
                sr += w * math.sin(2.0 * math.pi * (f * det) * t + 0.35 * fi)
            idx = (start_idx + k) % n
            left[idx] += env * breath * sl
            right[idx] += env * breath * sr

        note_step = bar_sec / (len(piano_notes) + 0.35)
        for ni, nf in enumerate(piano_notes):
            note_start = int((bar_start_s + 0.30 + ni * note_step) * SR)
            note_n = int(3.2 * SR)
            pan = -0.22 + 0.44 * (ni / max(1, len(piano_notes) - 1))
            gl = math.cos((pan + 1.0) * math.pi * 0.25)
            gr = math.sin((pan + 1.0) * math.pi * 0.25)
            vel = 0.24 if ni == 0 else 0.18
            for k in range(note_n):
                t = k / SR
                env = min(1.0, t / 0.018) * math.exp(-t * 1.45)
                tone = (
                    math.sin(2.0 * math.pi * nf * t)
                    + 0.24 * math.sin(2.0 * math.pi * nf * 2.0 * t) * math.exp(-t * 3.2)
                    + 0.07 * math.sin(2.0 * math.pi * nf * 3.0 * t) * math.exp(-t * 6.5)
                )
                idx = (note_start + k) % n
                val = vel * env * tone
                left[idx] += val * gl
                right[idx] += val * gr

    tmp_wav = write_wav_stereo(out_dir, "_tmp_ambient_bed.wav", left, right, peak=0.68, fade_edges=False)
    mp3_path = out_dir / "ambient_bed.mp3"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(tmp_wav),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(mp3_path),
        ],
        check=True,
    )
    os.remove(tmp_wav)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Synthesize 12 warm studio WAV SFX + 45s loopable ambient_bed.mp3."
    )
    p.add_argument(
        "--out-dir",
        default=Path("public/sfx"),
        type=Path,
        help="Destination SFX directory (default: ./public/sfx).",
    )
    p.add_argument(
        "--skip-ambient",
        action="store_true",
        help="Generate only the 12 WAV SFX without encoding ambient_bed.mp3 (skips ffmpeg).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    for fn in (
        gen_whoosh_velvet,
        gen_whoosh_cinematic,
        gen_pop_wood,
        gen_pop_bubble,
        gen_boing_soft,
        gen_chime_warm,
        gen_sparkle_magic,
        gen_rope_tug,
        gen_snip_crisp,
        gen_stamp_thud,
        gen_alert_soft,
        gen_page_turn,
    ):
        fn(out_dir)

    if not args.skip_ambient:
        gen_ambient_bed(out_dir)
        print(f"Synthesized 12 studio WAV SFX + ambient_bed.mp3 -> {out_dir}")
    else:
        print(f"Synthesized 12 studio WAV SFX -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
