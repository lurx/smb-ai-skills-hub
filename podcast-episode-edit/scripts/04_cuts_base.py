#!/usr/bin/env python3
"""Stage 04: baseline cut decisions from per-camera motion signals.

Inputs:  motion_host.npy, motion_guest.npy, trim.txt, sync_offset.txt
Output:  cuts.json = timing header + baseline segments
         {"trim_in", "trim_out", "sync_offset", "duration",
          "segments": [{"t0","t1","cam":"host"|"guest"|"BOTH","duration"}]}
         Timestamps are SEQUENCE time (final output timeline, starting at 0).

Logic:
  1. Resample both motion signals onto the mic-cam timeline (trim range)
  2. Smooth with a 1.0 s rolling mean, normalise by each cam's own median
  3. Per 0.25 s bin decide: BOTH if both strongly active, else the louder
     cam with hysteresis (stay unless the other is 20% higher)
  4. Enforce a minimum shot length by merging short runs into the longer
     neighbour

The timing header written here is the anchor that EVERY later stage reads.
Stage 08 refines the segments with audio correlation; this baseline is also
what 07_find_hooks uses to know which stretches belong to the guest.
"""
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import Config, base_parser, require_file, save_json  # noqa: E402

FPS = 4  # samples per second in the motion signal


def smooth(x: np.ndarray, w: int) -> np.ndarray:
    k = np.ones(w) / w
    return np.convolve(x, k, mode="same")


def normalize(x: np.ndarray) -> np.ndarray:
    base = np.median(x[x > 0]) + 1e-6
    return x / base


def sample_signal(signal: np.ndarray, t_seconds: float) -> float:
    idx = int(round(t_seconds * FPS))
    if 0 <= idx < len(signal):
        return float(signal[idx])
    return 0.0


def merge_short_runs(runs, min_samples):
    changed = True
    while changed:
        changed = False
        for k in range(len(runs)):
            cam, s, e = runs[k]
            if e - s >= min_samples:
                continue
            left = runs[k - 1] if k > 0 else None
            right = runs[k + 1] if k < len(runs) - 1 else None
            if left and right:
                target = left if (left[2] - left[1]) >= (right[2] - right[1]) else right
            elif left:
                target = left
            elif right:
                target = right
            else:
                break
            runs[k][0] = target[0]
            changed = True
            break
        new_runs = []
        for r in runs:
            if new_runs and new_runs[-1][0] == r[0]:
                new_runs[-1][2] = r[2]
            else:
                new_runs.append(list(r))
        runs = new_runs
    return runs


def main() -> None:
    ap = base_parser(__doc__)
    args = ap.parse_args()
    cfg = Config(args.config)
    P = cfg.paths()
    mic, other = cfg.mic_cam, cfg.other_cam

    m_mic = np.load(require_file(P[f"motion_{mic}"], "03_motion.py")).astype(np.float32)
    m_oth = np.load(require_file(P[f"motion_{other}"], "03_motion.py")).astype(np.float32)
    with open(require_file(P["sync_offset"], "01_sync.py")) as f:
        sync_off = float(f.read().strip())  # mic_t = other_t + sync_off
    with open(require_file(P["trim"], "02_trim.py")) as f:
        t_in, t_out = [float(x) for x in f.read().strip().split()]

    print(f"sync_offset ({mic} - {other}): {sync_off:+.3f}s")
    print(f"trim ({mic}): in={t_in:.2f}s  out={t_out:.2f}s  duration={(t_out-t_in):.2f}s")

    n_samples = int(round((t_out - t_in) * FPS))
    print(f"trimmed timeline samples ({FPS} fps): {n_samples}  ({n_samples/FPS/60:.2f} min)")
    s_oth = np.zeros(n_samples, dtype=np.float32)
    s_mic = np.zeros(n_samples, dtype=np.float32)
    for i in range(n_samples):
        t_m = t_in + i / FPS          # time on mic timeline
        t_o = t_m - sync_off          # time on other cam timeline
        s_oth[i] = sample_signal(m_oth, t_o)
        s_mic[i] = sample_signal(m_mic, t_m)

    n_oth = normalize(smooth(s_oth, FPS))
    n_mic = normalize(smooth(s_mic, FPS))
    print(f"{other} normalized: median={np.median(n_oth):.2f}  p90={np.percentile(n_oth, 90):.2f}  max={n_oth.max():.2f}")
    print(f"{mic} normalized: median={np.median(n_mic):.2f}  p90={np.percentile(n_mic, 90):.2f}  max={n_mic.max():.2f}")

    T_SPEAK = float(cfg.get("cuts.speak_threshold"))
    T_BOTH = float(cfg.get("cuts.both_threshold"))
    decisions = np.empty(n_samples, dtype=object)
    prev_cam = "host"  # start on the host
    for i in range(n_samples):
        a = n_oth[i]; b = n_mic[i]
        if a > T_BOTH and b > T_BOTH:
            cam = "BOTH"
        elif a > T_SPEAK and b > T_SPEAK:
            if a > b * 1.2: cam = other
            elif b > a * 1.2: cam = mic
            else: cam = prev_cam
        elif a > T_SPEAK:
            cam = other
        elif b > T_SPEAK:
            cam = mic
        else:
            cam = prev_cam
        decisions[i] = cam
        prev_cam = cam if cam != "BOTH" else prev_cam

    runs = []
    i = 0
    while i < n_samples:
        j = i
        while j < n_samples and decisions[j] == decisions[i]:
            j += 1
        runs.append([decisions[i], i, j])
        i = j
    runs = merge_short_runs(runs, int(float(cfg.get("cuts.baseline_min_shot_seconds")) * FPS))

    segments = []
    for cam, s, e in runs:
        t0, t1 = s / FPS, e / FPS
        segments.append({"t0": round(t0, 3), "t1": round(t1, 3), "cam": cam, "duration": round(t1 - t0, 3)})

    doc = {
        "mic_cam": mic,
        "trim_in": t_in,
        "trim_out": t_out,
        "sync_offset": sync_off,
        "duration": round(t_out - t_in, 3),
        "segments": segments,
    }
    save_json(P["cuts"], doc)

    cam_time = Counter()
    for s in segments:
        cam_time[s["cam"]] += s["duration"]
    total = sum(cam_time.values())
    print(f"\nshots: {len(segments)}")
    print(f"avg shot duration: {total/len(segments):.1f}s")
    for cam, t in cam_time.most_common():
        print(f"  {cam:6s}: {t:7.1f}s ({100*t/total:.1f}%)")
    print(f"\nwrote {P['cuts']}")


if __name__ == "__main__":
    main()
