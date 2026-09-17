#!/usr/bin/env python3
"""Fail if any cut lands in the middle of a word.

Every segment boundary in a ReelConfig is an audio splice. If speech is still
running there, the word is chopped — the most audible defect a reel can have.
This measures the waveform rather than trusting transcript word timings, which
drift by tens of milliseconds.

LIMITATION, stated plainly: this catches a cut through a vowel, which is the
common error. It does NOT catch a cut through a stop consonant (ק, ת, ב, פ),
whose silent closure reads as a clean gap while the release burst that
completes the word still lies ahead. That is how "השיווק" once shipped as
"השיוו" with every check green.

Detecting that automatically was tried and abandoned: a stop release and the
onset of the next word are the same shape after a pause, so the warning fired
on five of eight known-good cuts. A warning that fires on everything teaches
you to ignore it.

  These levels are necessary, not sufficient.
  Listen to the last word before every cut.

Usage:  python3 check-cuts.py [reel-number ...]      (default: all)
Run from the project root. Exit code 1 if any cut is dirty.
"""
import glob
import os
import re
import sys

import numpy as np

from _ff import load_audio, rms as _rms

# RMS over a 40ms window below this counts as "not speech". Calibrated against
# a real podcast: between-word gaps sit at 0.001-0.03, running speech at
# 0.05-0.20. Recalibrate for a much quieter or noisier recording.
SILENCE = 0.035
WINDOW = 0.04

ROOT = os.getcwd()


def rms_at(a, sr, t, side="center"):
    """RMS around t. One-sided on purpose.

    An end-cut asks "was something still playing up to here", so it looks back.
    A start-cut asks "does sound begin abruptly here", so it looks forward. A
    centred window straddles the splice and counts the next syllable as if it
    were the current word — a bug that hid a dirty cut until it was fixed.
    """
    if side == "before":
        s, e = int((t - WINDOW) * sr), int(t * sr)
    elif side == "after":
        s, e = int(t * sr), int((t + WINDOW) * sr)
    else:
        s, e = int((t - WINDOW / 2) * sr), int((t + WINDOW / 2) * sr)
    s, e = max(0, s), min(len(a), e)
    return _rms(a[s:e])


def nearest_quiet(a, sr, t, side, radius=0.5):
    best, best_r = None, 1e9
    for i in range(-int(radius * 100), int(radius * 100) + 1):
        cand = t + i * 0.01
        if cand < 0 or cand * sr >= len(a):
            continue
        r = rms_at(a, sr, cand, side)
        if r < best_r:
            best, best_r = cand, r
    return best, best_r


def parse_config(path):
    s = open(path, encoding="utf-8").read()
    cold = re.search(r"coldOpen: \{start: ([\d.]+), end: ([\d.]+)\}", s)
    # Scope to the body array. A loose {start:,end:} match also caught the
    # coldOpen line whenever a comment followed it.
    block = re.search(r"body: \[(.*?)\],\s*\n\s*warmth", s, re.S)
    body = re.findall(r"\{start: ([\d.]+), end: ([\d.]+)\}",
                      block.group(1) if block else "")
    src = re.search(r"source: '([^']+)'", s)
    cuts = []
    if cold:
        cuts += [("coldOpen.start", float(cold.group(1))),
                 ("coldOpen.end", float(cold.group(2)))]
    for i, (x, y) in enumerate(body):
        cuts += [(f"body[{i}].start", float(x)), (f"body[{i}].end", float(y))]
    return (src.group(1) if src else None), cuts


def main():
    wanted = sys.argv[1:]
    failed = False      # a cut is dirty
    unchecked = False   # a source is missing, so nothing could be measured

    configs = sorted(glob.glob(os.path.join(ROOT, "src/data/reel-*.ts")))
    if not configs:
        raise SystemExit("no src/data/reel-*.ts found — run from the project root")

    for cfg in configs:
        reel = re.search(r"reel-(\w+)\.ts", cfg).group(1)
        if wanted and reel not in wanted:
            continue
        source, cuts = parse_config(cfg)
        path = os.path.join(ROOT, "public", source or "")
        if not source or not os.path.exists(path):
            print(f"\nreel {reel}: public/{source} not found — nothing to measure.")
            print(f"  create it first:  ./scripts/prepare-source.sh <master>"
                  f" public/{source} <start> <dur> <crop> <scale>")
            unchecked = True
            continue

        a, sr = load_audio(path)
        dur = len(a) / sr
        print(f"\nreel {reel}  ({source}, {dur:.2f}s)")

        for name, t in cuts:
            if t > dur + 0.01:
                print(f"  x {name:16s} {t:6.2f}s  past the end of the source ({dur:.2f}s)")
                failed = True
                continue
            if t <= 0.02:
                print(f"  . {name:16s} {t:6.2f}s  start of file")
                continue
            side = "before" if name.endswith(".end") else "after"
            r = rms_at(a, sr, t, side)
            if r <= SILENCE:
                print(f"  v {name:16s} {t:6.2f}s  rms {r:.4f}")
            else:
                q, qr = nearest_quiet(a, sr, t, side)
                print(f"  x {name:16s} {t:6.2f}s  rms {r:.4f}  — MID-WORD."
                      f" nearest quiet: {q:.2f}s (rms {qr:.4f})")
                failed = True

    if failed:
        print("\nFAIL — a cut lands mid-word")
    elif unchecked:
        print("\nNOT CHECKED — a source file is missing (see above)")
    else:
        print("\nOK on levels — now listen to the last word before each cut")
    return 1 if (failed or unchecked) else 0


if __name__ == "__main__":
    sys.exit(main())
