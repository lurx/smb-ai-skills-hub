#!/usr/bin/env python3
"""Stage 09: render the episode BODY from the original camera files.

- single-camera segments from cuts_final.json (fallback: cuts.json with --cuts base)
- split-screen (host | guest, side by side) during:
    * the first split_screen.intro_seconds
    * split_screen.hook_seconds at the start of every hook in hooks.json
    * the last split_screen.outro_seconds
- cinematic curves + eq colour grade (config color_grade)
- audio = audio_track.m4a (mic camera)
- NO subtitles, NO lower third (those are separate optional stages)

The full filter graph is written to work/body_filter.txt and passed with
-filter_complex_script (command-line length limits would break otherwise).
Output: work/body.mp4 at the source resolution. Expect 1-2 hours for a 4K hour.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import (Config, base_parser, die, ffprobe_video, load_json,  # noqa: E402
                        require_file, require_tool, source_in_points)


def load_hooks(path: str):
    if not os.path.isfile(path):
        print(f"note: no hooks file at {path}; split-screen only at intro/outro")
        return []
    hooks = load_json(path)
    for h in hooks:
        for k in ("slug", "start", "end"):
            if k not in h:
                die(f"hooks.json entry missing '{k}': {h}")
    return hooks


def main() -> None:
    ap = base_parser(__doc__)
    ap.add_argument("--cuts", choices=["final", "base"], default="final")
    ap.add_argument("--dry-run", action="store_true", help="write the filter script, do not run ffmpeg")
    args = ap.parse_args()
    cfg = Config(args.config)
    require_tool("ffmpeg")
    P = cfg.paths()
    cuts_path = P["cuts_final"] if args.cuts == "final" else P["cuts"]
    doc = load_json(require_file(cuts_path, "08_cuts_audio_correlation.py" if args.cuts == "final" else "04_cuts_base.py"))
    audio = require_file(P["audio_track"], "05_proxies.sh")
    segments = doc["segments"]
    DURATION = float(doc["duration"])
    src_in = source_in_points(cfg, doc)
    fps = int(cfg.get("fps"))

    host_path, guest_path = cfg.cam_path("host"), cfg.cam_path("guest")
    info = ffprobe_video(host_path)
    W, H = info["width"], info["height"]
    print(f"source: {W}x{H}")

    # ---- split-screen ranges ----------------------------------------
    sp = cfg.get("split_screen")
    split_ranges = []
    if sp.get("enabled", True):
        intro_s, outro_s, hook_s = float(sp["intro_seconds"]), float(sp["outro_seconds"]), float(sp["hook_seconds"])
        if intro_s > 0:
            split_ranges.append((0.0, intro_s))
        for h in load_hooks(P["hooks"]):
            split_ranges.append((float(h["start"]), float(h["start"]) + hook_s))
        if outro_s > 0:
            split_ranges.append((DURATION - outro_s, DURATION))
        split_ranges.sort()
        for i in range(len(split_ranges) - 1):
            if split_ranges[i][1] > split_ranges[i + 1][0]:
                die(f"split-screen windows overlap: {split_ranges[i]} and {split_ranges[i+1]}. "
                    "move a hook start or shorten split_screen.hook_seconds")

    blocks = []

    def add_single(t_start, t_end):
        for seg in segments:
            if seg["t1"] <= t_start or seg["t0"] >= t_end:
                continue
            t0, t1 = max(seg["t0"], t_start), min(seg["t1"], t_end)
            if t1 - t0 > 0.001:
                cam = seg["cam"] if seg["cam"] in ("host", "guest") else "host"  # BOTH -> host
                blocks.append({"type": "single", "t0": t0, "t1": t1, "cam": cam})

    cursor = 0.0
    for s0, s1 in split_ranges:
        if cursor < s0 - 0.001:
            add_single(cursor, s0)
        blocks.append({"type": "split", "t0": s0, "t1": s1})
        cursor = s1
    if cursor < DURATION - 0.001:
        add_single(cursor, DURATION)
    n_split = sum(1 for b in blocks if b["type"] == "split")
    print(f"composing {len(blocks)} blocks: {len(blocks)-n_split} single + {n_split} split, {DURATION:.1f}s")

    # ---- filter graph -----------------------------------------------
    half_w = W // 2
    left_role = sp.get("left_cam", "host")
    right_role = "guest" if left_role == "host" else "host"
    crop = {}
    for r in ("host", "guest"):
        x = cfg.cam(r).get("split_crop_x")
        x = int(x) if x is not None else (W - half_w) // 2
        crop[r] = f"crop={half_w}:{H}:{x}:0"
    idx = {"host": 0, "guest": 1}

    chains, labels = [], []
    for i, b in enumerate(blocks):
        out = f"v{i}"
        if b["type"] == "single":
            r = b["cam"]
            chains.append(f"[{idx[r]}:v]trim={src_in[r]+b['t0']}:{src_in[r]+b['t1']},"
                          f"setpts=PTS-STARTPTS,setsar=1,fps={fps}[{out}]")
        else:
            parts = {}
            for r in (left_role, right_role):
                lab = f"{'L' if r == left_role else 'R'}{i}"
                chains.append(f"[{idx[r]}:v]trim={src_in[r]+b['t0']}:{src_in[r]+b['t1']},"
                              f"setpts=PTS-STARTPTS,{crop[r]},setsar=1,fps={fps}[{lab}]")
                parts[r] = lab
            chains.append(f"[{parts[left_role]}][{parts[right_role]}]hstack=inputs=2[{out}]")
        labels.append(f"[{out}]")
    chains.append("".join(labels) + f"concat=n={len(blocks)}:v=1:a=0[concat]")
    cg = cfg.get("color_grade")
    if cg.get("enabled", True):
        chains.append(f"[concat]{cg['curves']},{cg['eq']}[graded]")
    else:
        chains.append("[concat]null[graded]")

    with open(P["body_filter"], "w") as f:
        f.write(";\n".join(chains) + "\n")
    print(f"wrote filter script {P['body_filter']} ({len(chains)} chains)")
    if args.dry_run:
        return

    enc = cfg.get("encoder")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-stats", "-y",
           "-i", host_path, "-i", guest_path, "-i", audio,
           "-filter_complex_script", P["body_filter"],
           "-map", "[graded]", "-map", "2:a", "-t", f"{DURATION:.3f}",
           *cfg.video_codec_args(enc["body_bitrate"], enc["body_maxrate"], enc["body_bufsize"]),
           "-c:a", "aac", "-b:a", enc["audio_bitrate"],
           "-r", str(fps), "-movflags", "+faststart", P["body"]]
    print("rendering body (long)...")
    subprocess.run(cmd, check=True)
    print(f"done -> {P['body']}")


if __name__ == "__main__":
    main()
