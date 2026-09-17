#!/usr/bin/env python3
"""Stage 12: cut 9:16 reels from the episode (reels camera, mic audio).

For every hook in hooks.json ({"slug","start","end"} in sequence seconds,
optionally "ranges": [[t0,t1],...] for multi-range cuts):
  1. face-crop: a Haar cascade finds the face X in 3 sample frames per range,
     the median X centres a (height*9/16) x height crop; if no face is found
     the crop falls back to the frame centre
  2. pass 1: trim + crop + scale 1080x1920 (+ concat for multi-range)
  3. pass 2 (--subs, default): burn ASS captions with the "reel" preset
Output: work/reels/reel_<slug>.mp4 (+ .ass when subs are on)
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import (Config, base_parser, die, ffprobe_video, load_json,  # noqa: E402
                        require_file, require_tool, source_in_points)
from lib_captions import Fixes, group_for_preset, make_ass, preprocess_words, words_in_ranges  # noqa: E402


def hook_ranges(h):
    if "ranges" in h:
        return [[float(a), float(b)] for a, b in h["ranges"]]
    return [[float(h["start"]), float(h["end"])]]


def main() -> None:
    ap = base_parser(__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--subs", dest="subs", action="store_true", default=True, help="burn captions (default)")
    g.add_argument("--no-subs", dest="subs", action="store_false", help="no captions")
    ap.add_argument("--only", help="render only this slug")
    args = ap.parse_args()
    cfg = Config(args.config)
    require_tool("ffmpeg")
    P = cfg.paths()
    doc = load_json(require_file(P["cuts"], "04_cuts_base.py"))
    src_in = source_in_points(cfg, doc)
    audio = require_file(P["audio_track"], "05_proxies.sh")
    hooks = load_json(require_file(P["hooks"], "07_find_hooks.py (then write hooks.json by hand)"))
    if args.only:
        hooks = [h for h in hooks if h["slug"] == args.only] or die(f"no hook with slug {args.only}")
    cam = cfg.reels_cam
    cam_path = cfg.cam_path(cam)
    cam_in = src_in[cam]
    info = ffprobe_video(cam_path)
    FW, FH = info["width"], info["height"]
    CROP_H = FH
    CROP_W = int(round(FH * 9 / 16))
    fps = int(cfg.get("fps"))
    enc = cfg.get("encoder")
    out_dir = P["reels_dir"]
    os.makedirs(out_dir, exist_ok=True)

    words = None
    fixes = None
    if args.subs:
        words = load_json(require_file(P["whisper"], "06_transcribe.py"))["words"]
        fixes = Fixes.load(P["fixes"])

    try:
        import cv2
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    except ImportError:
        cv2 = None
        cascade = None
        print("warning: opencv-python not installed; using centre crop")

    def detect_face_x(seq_t):
        if cascade is None:
            return None
        fd, tmp = tempfile.mkstemp(suffix=".jpg"); os.close(fd)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{cam_in + seq_t}", "-i", cam_path,
                        "-frames:v", "1", "-vf", "scale=960:-2", tmp], check=True)
        img = cv2.imread(tmp); os.remove(tmp)
        if img is None:
            return None
        faces = cascade.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.1, 5, minSize=(80, 80))
        if not len(faces):
            return None
        f = max(faces, key=lambda r: r[2] * r[3])   # largest face
        return (f[0] + f[2] / 2) * (FW / 960)

    def median_face_x(ranges):
        xs = []
        for t0, t1 in ranges:
            for k in range(3):
                x = detect_face_x(t0 + (t1 - t0) * (k + 0.5) / 3)
                if x is not None:
                    xs.append(x)
        if not xs:
            return FW / 2   # derived fallback: frame centre
        xs.sort()
        return xs[len(xs) // 2]

    for h in hooks:
        slug = h["slug"]
        ranges = hook_ranges(h)
        fx = median_face_x(ranges)
        crop_x = max(0, min(int(fx - CROP_W / 2), FW - CROP_W))
        total = sum(t1 - t0 for t0, t1 in ranges)

        inputs, fparts = [], []
        for ri, (t0, t1) in enumerate(ranges):
            seg_dur = t1 - t0
            inputs += ["-ss", f"{cam_in + t0:.3f}", "-i", cam_path, "-ss", f"{t0:.3f}", "-i", audio]
            v_in, a_in = ri * 2, ri * 2 + 1
            fparts.append(f"[{v_in}:v]trim=duration={seg_dur:.3f},setpts=PTS-STARTPTS,"
                          f"crop={CROP_W}:{CROP_H}:{crop_x}:0,scale=1080:1920,setsar=1,fps={fps}[v{ri}]")
            fparts.append(f"[{a_in}:a]atrim=duration={seg_dur:.3f},asetpts=PTS-STARTPTS[a{ri}]")
        if len(ranges) == 1:
            v_label, a_label = "[v0]", "[a0]"
        else:
            cat = "".join(f"[v{i}][a{i}]" for i in range(len(ranges)))
            fparts.append(f"{cat}concat=n={len(ranges)}:v=1:a=1[outv][outa]")
            v_label, a_label = "[outv]", "[outa]"

        out_path = os.path.join(out_dir, f"reel_{slug}.mp4")
        codec = cfg.video_codec_args(enc["reel_bitrate"])
        base = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-stats", "-y"]
        pass1_out = os.path.join(out_dir, f"_tmp_{slug}.mp4") if args.subs else out_path
        print(f"[{slug}]  {total:.1f}s  crop_x={crop_x}  subs={'on' if args.subs else 'off'}")
        subprocess.run(base + inputs + ["-filter_complex", ";".join(fparts), "-map", v_label, "-map", a_label,
                                        *codec, "-c:a", "aac", "-b:a", enc["audio_bitrate"],
                                        "-r", str(fps), "-movflags", "+faststart", pass1_out], check=True)
        if not args.subs:
            continue
        local = words_in_ranges(words, ranges)
        groups = group_for_preset(preprocess_words(local, fixes), "reel")
        ass_path = os.path.join(out_dir, f"reel_{slug}.ass")
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(make_ass(groups, total, "reel", cfg.get("fonts.caption_font_name"), fixes))
        print(f"    {len(groups)} caption groups -> burning")
        subprocess.run(base + ["-i", pass1_out, "-vf", f"subtitles={ass_path}", *codec,
                               "-c:a", "copy", "-r", str(fps), "-movflags", "+faststart", out_path], check=True)
        os.remove(pass1_out)

    print(f"\n=== DONE === {out_dir}")
    for f in sorted(os.listdir(out_dir)):
        if f.endswith(".mp4"):
            print(f"  {f}  ({os.path.getsize(os.path.join(out_dir, f))/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
