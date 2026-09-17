#!/usr/bin/env python3
"""Stage 01: find the time offset between the two cameras by
cross-correlating their 8 kHz mono audio (from 00_extract_audio.sh).

Writes sync_offset.txt = (mic cam time) - (other cam time), in seconds.
Positive = the mic camera started recording AFTER the other camera.
"""
import os
import sys

import numpy as np
from scipy.signal import correlate, correlation_lags

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import Config, base_parser, require_file  # noqa: E402

SR = 8000


def main() -> None:
    ap = base_parser(__doc__)
    args = ap.parse_args()
    cfg = Config(args.config)
    P = cfg.paths()
    other, mic = cfg.other_cam, cfg.mic_cam
    a = np.fromfile(require_file(P[f"pcm_{other}"], "00_extract_audio.sh"), dtype=np.int16).astype(np.float32)
    b = np.fromfile(require_file(P[f"pcm_{mic}"], "00_extract_audio.sh"), dtype=np.int16).astype(np.float32)
    print(f"{other} audio len: {len(a)/SR:.2f}s")
    print(f"{mic} audio len: {len(b)/SR:.2f}s")

    # Normalise
    a -= a.mean(); b -= b.mean()
    a /= (a.std() + 1e-9); b /= (b.std() + 1e-9)

    # Use a window from the middle of both (avoid silent heads/tails)
    WIN = int(cfg.get("sync.window_seconds")) * SR
    mid_a = len(a) // 2
    mid_b = len(b) // 2
    a_win = a[max(0, mid_a - WIN // 2): mid_a + WIN // 2]
    b_win = b[max(0, mid_b - WIN // 2): mid_b + WIN // 2]

    print("running cross-correlation (this takes a moment)...")
    corr = correlate(b_win, a_win, mode="full", method="fft")
    lags = correlation_lags(len(b_win), len(a_win), mode="full")
    peak = int(np.argmax(corr))
    lag_samples = int(lags[peak])
    # Both windows were sliced around their own middles; convert the window
    # lag back to a global offset between the original streams.
    global_lag = (mid_b - WIN // 2) - (mid_a - WIN // 2) + lag_samples
    offset_seconds = global_lag / SR
    print(f"window cross-corr peak lag: {lag_samples} samples ({lag_samples/SR:+.4f}s)")
    print(f"global offset ({mic} - {other}): {global_lag} samples ({offset_seconds:+.4f}s)")

    with open(P["sync_offset"], "w") as f:
        f.write(f"{offset_seconds:.6f}\n")
    print(f"\nwrote {P['sync_offset']} = {offset_seconds:+.4f}s")


if __name__ == "__main__":
    main()
