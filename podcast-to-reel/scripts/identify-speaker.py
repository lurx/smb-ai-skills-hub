#!/usr/bin/env python3
"""Who is speaking, measured from the audio.

Estimates fundamental frequency (F0) by autocorrelation and reports it per
second. Male voices sit at 85-155 Hz, female at 165-255 Hz.

NEVER identify a speaker from motion in the video. A listener nodding at a
closer camera out-registers the actual speaker; that mistake cost a whole
rebuild in the project this came from.

Per-second resolution is deliberate. Summarising over 5-second windows once
reported "a single speaker throughout" for a clip that opened with the
interviewer's question.

Usage:  python3 identify-speaker.py <clip> [male-female-split-hz]
"""
import sys

import numpy as np

from _ff import load_audio, rms

WIN = 0.04       # autocorrelation window
MIN_VOICED = 5   # 10ms sub-frames needed before a second counts as speech


def f0(seg, sr, lo=70, hi=320):
    seg = seg - seg.mean()
    if rms(seg) < 0.02:
        return None
    c = np.correlate(seg, seg, "full")[len(seg) - 1:]
    if c[0] <= 0:
        return None
    c /= c[0]
    lag_lo, lag_hi = int(sr / hi), int(sr / lo)
    region = c[lag_lo:lag_hi]
    if not len(region):
        return None
    lag = lag_lo + int(np.argmax(region))
    return sr / lag if c[lag] > 0.3 else None


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = sys.argv[1]
    split = float(sys.argv[2]) if len(sys.argv) > 2 else 160.0

    a, sr = load_audio(path)
    dur = len(a) / sr
    win, hop = int(WIN * sr), int(0.02 * sr)

    marks, all_vals = [], []
    for s in range(int(dur)):
        vals = [v for i in range(s * sr, (s + 1) * sr - win, hop)
                if (v := f0(a[i:i + win], sr))]
        all_vals += vals
        if len(vals) < MIN_VOICED:
            marks.append(".")
        else:
            marks.append("M" if float(np.median(vals)) < split else "F")

    m, f = marks.count("M"), marks.count("F")
    med = float(np.median(all_vals)) if all_vals else 0.0

    print(f"{path}")
    print(f"  length        {dur:.1f}s")
    print(f"  median F0     {med:.1f} Hz")
    print(f"  male seconds  {m}")
    print(f"  female seconds{f:>4}")
    print(f"\n  {''.join(marks)}")
    print("  M = male second, F = female, . = too little voiced audio\n")

    if m and f:
        runs = [i for i, c in enumerate(marks)
                if c == ("M" if m < f else "F")
                and (i == 0 or marks[i - 1] != c)]
        minority = "male" if m < f else "female"
        print(f"  MIXED clip. {minority} seconds begin at: {runs}")
        print("  Cropping to one speaker will desync picture from voice there.")
        if marks and marks[0] == ("M" if m < f else "F"):
            print("  NOTE: the clip OPENS with the minority speaker.")
    elif m or f:
        print(f"  Single speaker: {'male' if m else 'female'}.")
    else:
        print("  No voiced audio detected.")


if __name__ == "__main__":
    main()
