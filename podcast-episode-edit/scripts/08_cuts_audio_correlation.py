#!/usr/bin/env python3
"""Stage 08: refine camera switches with AUDIO-MOTION CORRELATION.

The speaker's camera has face motion that correlates with the audio
amplitude (mouth moves when sound is produced); the listener's motion is
uncorrelated. For each Whisper segment:
  - audio RMS per 250 ms inside the segment (from audio_track.m4a)
  - both cameras' motion inside the segment (already 4 fps = 250 ms)
  - Pearson correlation audio<->motion per camera
  - pick the camera with the higher correlation (margin + hysteresis)
Then fill gaps, collapse neighbours, enforce min shot length.
Writes cuts_final.json (same header as cuts.json, new segments).
"""
import os
import subprocess
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import (Config, base_parser, load_json, require_file,  # noqa: E402
                        require_tool, save_json, source_in_points)

FPS = 4


def enforce_min(shots, min_len):
    changed = True
    while changed:
        changed = False
        for i, (s, e, cam) in enumerate(shots):
            if e - s >= min_len:
                continue
            left = shots[i - 1] if i > 0 else None
            right = shots[i + 1] if i < len(shots) - 1 else None
            if left and right:
                target = left if (left[1] - left[0]) >= (right[1] - right[0]) else right
            else:
                target = left or right
            if target:
                shots[i] = [s, e, target[2]]
                changed = True
                break
        new = []
        for s, e, cam in shots:
            if new and new[-1][2] == cam:
                new[-1][1] = e
            else:
                new.append([s, e, cam])
        shots = new
    return shots


def pearson(x, y):
    if x.std() < 1e-9 or y.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def main() -> None:
    ap = base_parser(__doc__)
    args = ap.parse_args()
    cfg = Config(args.config)
    require_tool("ffmpeg")
    P = cfg.paths()
    doc = load_json(require_file(P["cuts"], "04_cuts_base.py"))
    DURATION = doc["trim_out"] - doc["trim_in"]
    W = load_json(require_file(P["whisper"], "06_transcribe.py"))
    audio = require_file(P["audio_track"], "05_proxies.sh")

    print("computing audio RMS per 250ms...")
    sr = 16000
    hop = sr // 4
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", audio,
                           "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                          check=True, capture_output=True)
    samples = np.frombuffer(proc.stdout, dtype=np.float32)
    n_frames = len(samples) // hop
    arms = np.sqrt(np.mean(samples[:n_frames * hop].reshape(n_frames, hop) ** 2, axis=1))
    print(f"audio frames: {n_frames}, duration: {n_frames*hop/sr:.1f}s")

    motion = {r: np.load(require_file(P[f"motion_{r}"], "03_motion.py")).astype(np.float32)
              for r in ("host", "guest")}
    src_in = source_in_points(cfg, doc)
    host, guest = "host", "guest"
    margin = float(cfg.get("cuts.correlation_margin"))
    min_seg = float(cfg.get("cuts.min_segment_seconds"))

    def window(t0, t1):
        n = int(round((t1 - t0) * 4))
        if n < 4:
            return None
        a0 = int(round(t0 * 4))
        a_win = arms[a0:a0 + n]
        wins = {}
        for r in (host, guest):
            m0 = int(round((src_in[r] + t0) * FPS))
            wins[r] = motion[r][m0:m0 + n]
        k = min(len(a_win), len(wins[host]), len(wins[guest]))
        if k < 4:
            return None
        return a_win[:k], wins[host][:k], wins[guest][:k]

    prev_cam = host
    shots = []
    for seg in W["segments"]:
        t0 = max(0.0, seg["start"]); t1 = min(DURATION, seg["end"])
        if t1 - t0 < min_seg:
            continue
        win = window(t0, t1)
        c_host = c_guest = 0.0
        if win is not None:
            a_w, h_w, g_w = win
            c_host, c_guest = pearson(a_w, h_w), pearson(a_w, g_w)
        if c_guest > c_host + margin:
            cam = guest
        elif c_host > c_guest + margin:
            cam = host
        else:
            cam = prev_cam
        shots.append([t0, t1, cam])
        prev_cam = cam

    filled, last_end = [], 0.0
    for s, e, cam in shots:
        if s > last_end + 0.05:
            filled.append([last_end, s, filled[-1][2] if filled else host])
        filled.append([s, e, cam])
        last_end = e
    if last_end < DURATION:
        filled.append([last_end, DURATION, filled[-1][2] if filled else host])

    collapsed = []
    for s, e, cam in filled:
        if collapsed and collapsed[-1][2] == cam:
            collapsed[-1][1] = e
        else:
            collapsed.append([s, e, cam])
    collapsed = enforce_min(collapsed, float(cfg.get("cuts.min_shot_seconds")))

    cam_time = Counter()
    for s, e, cam in collapsed:
        cam_time[cam] += e - s
    total = sum(cam_time.values())
    print(f"\nshots: {len(collapsed)}, avg {total/len(collapsed):.1f}s")
    for cam, t in cam_time.most_common():
        print(f"  {cam}: {t:.1f}s ({100*t/total:.1f}%)")

    out = dict(doc)
    out["segments"] = [{"t0": round(s, 3), "t1": round(e, 3), "cam": cam, "duration": round(e - s, 3)}
                       for s, e, cam in collapsed]
    save_json(P["cuts_final"], out)
    print(f"\nwrote {P['cuts_final']}")


if __name__ == "__main__":
    main()
