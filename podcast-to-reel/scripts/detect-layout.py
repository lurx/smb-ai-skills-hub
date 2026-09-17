#!/usr/bin/env python3
"""Find the split-screen geometry of a Zoom-style recording.

Reports the letterbox bounds and the seam between speaker tiles, so the crop
can be measured rather than guessed. Black bars and seam positions differ
between recordings.

Usage:  python3 detect-layout.py <video> [sample-second]
"""
import subprocess
import sys

import numpy as np

from _ff import ffmpeg


def frame_gray(path, t):
    p = subprocess.run(
        [ffmpeg(), "-v", "error", "-ss", str(t), "-i", str(path),
         "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True,
    )
    return p.stdout


def dimensions(path):
    p = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True)
    for line in p.stderr.splitlines():
        if "Video:" in line:
            for tok in line.split(","):
                tok = tok.strip().split(" ")[0]
                if "x" in tok:
                    try:
                        w, h = tok.split("x")
                        return int(w), int(h)
                    except ValueError:
                        continue
    raise SystemExit("could not read video dimensions")


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = sys.argv[1]
    t = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0

    w, h = dimensions(path)
    raw = frame_gray(path, t)
    if len(raw) < w * h:
        raise SystemExit(f"short frame at t={t}; try another sample second")
    a = np.frombuffer(raw[: w * h], dtype=np.uint8).reshape(h, w)

    THRESH = 18  # above this a pixel is content, not letterbox
    rows = np.where(a.max(axis=1) > THRESH)[0]
    cols = np.where(a.max(axis=0) > THRESH)[0]
    if not len(rows) or not len(cols):
        raise SystemExit("frame looks entirely black; try another sample second")

    top, bottom = int(rows.min()), int(rows.max())
    left, right = int(cols.min()), int(cols.max())
    strip_h = bottom - top + 1
    strip_w = right - left + 1

    print(f"video            {w}x{h}")
    print(f"content rows     {top}..{bottom}   (height {strip_h})")
    print(f"content cols     {left}..{right}   (width {strip_w})")

    # The seam between two tiles is the darkest column inside the strip.
    prof = a[top:bottom + 1, left:right + 1].mean(axis=0)
    mid_lo, mid_hi = int(strip_w * 0.35), int(strip_w * 0.65)
    seam = left + mid_lo + int(np.argmin(prof[mid_lo:mid_hi]))
    print(f"seam column      {seam}")

    lw, rw = seam - left, right - seam
    print(f"\nleft tile        ~{lw}x{strip_h}")
    print(f"right tile       ~{rw}x{strip_h}")

    print("\nsuggested crops (trim the bottom yourself if a name bar sits there):")
    print(f"  left   crop={lw}:{strip_h}:{left}:{top}")
    print(f"  right  crop={rw}:{strip_h}:{seam}:{top}")
    up = 1080 / max(lw, rw)
    print(f"\nscaling a tile to 1080 wide is {up:.2f}x."
          f"  {'fine' if up < 2.5 else 'SOFT — use a centred card, not full-bleed'}")
    print("output height must be even, or libx264 rejects it under yuv420p")


if __name__ == "__main__":
    main()
