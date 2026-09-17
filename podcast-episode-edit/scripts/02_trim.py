#!/usr/bin/env python3
"""Stage 02: Voice Activity Detection on the MIC camera audio to find the
episode in/out points.

RMS energy per 100 ms frame, frames above (noise floor + N dB) are 'voiced',
then the first and last window with >=60% voice within 5 s mark the episode.
Writes trim.txt = "<in> <out>" in seconds on the mic camera's timeline.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import Config, base_parser, die, require_file  # noqa: E402

SR = 8000
HOP = SR // 10  # 100 ms frames


def main() -> None:
    ap = base_parser(__doc__)
    args = ap.parse_args()
    cfg = Config(args.config)
    P = cfg.paths()
    pcm = require_file(P[f"pcm_{cfg.mic_cam}"], "00_extract_audio.sh")
    a = np.fromfile(pcm, dtype=np.int16).astype(np.float32) / 32768.0

    n = len(a) // HOP
    frames = a[:n * HOP].reshape(n, HOP)
    rms = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)

    floor = np.percentile(db, 5)
    threshold = floor + float(cfg.get("trim.voice_db_above_floor"))
    print(f"noise floor (p5):       {floor:6.2f} dB")
    print(f"voice threshold:        {threshold:6.2f} dB")
    print(f"max frame energy:       {db.max():6.2f} dB")
    print(f"median frame energy:    {np.median(db):6.2f} dB")

    voiced = db > threshold
    win = 50  # 5 s @ 100 ms hops
    kernel = np.ones(win) / win
    voiced_pct = np.convolve(voiced.astype(np.float32), kernel, mode="same")
    substantial = voiced_pct > 0.6

    where = np.flatnonzero(substantial)
    if len(where) == 0:
        die("no substantial voice activity detected on the mic camera")

    t_in = where[0] * 0.1
    t_out = (where[-1] + 1) * 0.1
    t_in = max(0.0, t_in - float(cfg.get("trim.pad_before")))
    t_out = min(len(a) / SR, t_out + float(cfg.get("trim.pad_after")))

    print(f"\nepisode start ({cfg.mic_cam} ts): {t_in:8.2f}s  ({t_in/60:.2f} min)")
    print(f"episode end   ({cfg.mic_cam} ts): {t_out:8.2f}s  ({t_out/60:.2f} min)")
    print(f"episode length:           {(t_out - t_in):8.2f}s ({(t_out - t_in)/60:.2f} min)")

    with open(P["trim"], "w") as f:
        f.write(f"{t_in:.3f} {t_out:.3f}\n")
    print(f"\nwrote {P['trim']}  (edit by hand if the detected points are off)")


if __name__ == "__main__":
    main()
