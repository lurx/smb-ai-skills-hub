#!/usr/bin/env python3
"""Stage 03: extract a face-region motion signal from each camera.

ffmpeg crops each camera's face ROI (from config), scales to 64x64 gray at
4 fps and pipes raw bytes here. Frame-to-frame absolute difference = motion.
High motion = mouth/head moving = probably speaking. Both cameras run in
parallel threads. Writes motion_<role>.npy (float32, 4 samples/second).
"""
import os
import subprocess
import sys
import threading
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import Config, base_parser, require_tool  # noqa: E402

FPS = 4
W = H = 64
PIX = W * H


def roi_filter(roi: dict) -> str:
    """roi = {x, y, w, h} as fractions of the frame."""
    for k in ("x", "y", "w", "h"):
        if k not in roi:
            raise SystemExit(f"face_roi must contain x, y, w, h (fractions 0..1); missing {k}")
    return (f"crop=in_w*{roi['w']}:in_h*{roi['h']}:in_w*{roi['x']}:in_h*{roi['y']},"
            f"scale={W}:{H},format=gray,fps={FPS}")


def run_cam(role: str, path: str, vf: str, out_path: str) -> None:
    print(f"[{role}] decoding ROI at {FPS} fps -> {W}x{H} gray ...")
    t0 = time.time()
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path, "-an",
           "-vf", vf, "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1"]
    proc = subprocess.run(cmd, check=True, capture_output=True)
    raw = proc.stdout
    nframes = len(raw) // PIX
    arr = np.frombuffer(raw, dtype=np.uint8, count=nframes * PIX).reshape(nframes, H, W).astype(np.int16)
    print(f"[{role}] decoded {nframes} frames ({nframes/FPS:.1f}s) in {time.time()-t0:.1f}s")
    diff = np.abs(np.diff(arr, axis=0)).astype(np.float32)
    motion = diff.sum(axis=(1, 2))
    motion = np.concatenate([[0.0], motion])  # align index i to time i/FPS
    np.save(out_path, motion.astype(np.float32))
    print(f"[{role}] saved {out_path}  (samples={len(motion)}, max={motion.max():.0f}, p95={np.percentile(motion, 95):.0f})")


def main() -> None:
    ap = base_parser(__doc__)
    args = ap.parse_args()
    cfg = Config(args.config)
    require_tool("ffmpeg")
    P = cfg.paths()
    threads = []
    for role in ("host", "guest"):
        cam = cfg.cam(role)
        roi = cam.get("face_roi") or {"x": 0.25, "y": 0.05, "w": 0.5, "h": 0.5}
        t = threading.Thread(target=run_cam, args=(role, cfg.cam_path(role), roi_filter(roi), P[f"motion_{role}"]))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print("\nmotion extraction done.")


if __name__ == "__main__":
    main()
