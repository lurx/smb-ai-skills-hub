#!/usr/bin/env python3
"""Stage 14 (optional): full-episode ASS captions from whisper.json.

Uses the shared caption module with the "1080p" or "4k" preset (3-word
groups, bottom centre). Times are sequence time, i.e. they line up with
body.mp4. If an intro was added in 11_concat.sh, pass --offset <intro
seconds> (or let the script read it from intro.mp4 with --offset auto).
--burn writes final_subs.mp4 from final.mp4 (or body.mp4 with --on body).
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import (Config, base_parser, ffprobe_duration, load_json,  # noqa: E402
                        require_file, require_tool)
from lib_captions import Fixes, group_for_preset, make_ass, preprocess_words  # noqa: E402


def main() -> None:
    ap = base_parser(__doc__)
    ap.add_argument("--res", choices=["1080p", "4k"], default="4k")
    ap.add_argument("--offset", default="auto",
                    help="seconds to shift captions (intro length). 'auto' = duration of intro.mp4 if it exists, else 0")
    ap.add_argument("--burn", action="store_true", help="burn into the video -> final_subs.mp4")
    ap.add_argument("--on", choices=["final", "body"], default="final", help="which video to burn on")
    args = ap.parse_args()
    cfg = Config(args.config)
    P = cfg.paths()
    doc = load_json(require_file(P["cuts"], "04_cuts_base.py"))
    DURATION = float(doc["duration"])
    words = load_json(require_file(P["whisper"], "06_transcribe.py"))["words"]
    fixes = Fixes.load(P["fixes"])

    if args.offset == "auto":
        offset = ffprobe_duration(P["intro"]) if (args.on == "final" and os.path.isfile(P["intro"])) else 0.0
    else:
        offset = float(args.offset)

    local = [{"word": w["word"], "start": w["start"] + offset, "end": w["end"] + offset}
             for w in words if 0 <= w["start"] < DURATION]
    groups = group_for_preset(preprocess_words(local, fixes), args.res)
    ass = make_ass(groups, DURATION + offset, args.res, cfg.get("fonts.caption_font_name"), fixes)
    with open(P["full_subs"], "w", encoding="utf-8") as f:
        f.write(ass)
    print(f"full episode: {len(local)} words -> {len(groups)} caption groups (offset {offset:.2f}s)")
    print(f"wrote {P['full_subs']}")

    if args.burn:
        require_tool("ffmpeg")
        src = require_file(P["final"] if args.on == "final" else P["body"],
                           "11_concat.sh" if args.on == "final" else "09_render_body.py")
        out = cfg.out("final_subs.mp4" if args.on == "final" else "body_subs.mp4")
        enc = cfg.get("encoder")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "warning", "-stats", "-y", "-i", src,
                        "-vf", f"subtitles={P['full_subs']}",
                        *cfg.video_codec_args(enc["body_bitrate"], enc["body_maxrate"], enc["body_bufsize"]),
                        "-c:a", "copy", "-movflags", "+faststart", out], check=True)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
