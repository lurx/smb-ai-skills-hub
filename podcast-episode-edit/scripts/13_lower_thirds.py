#!/usr/bin/env python3
"""Stage 13 (optional): lower-third PNG with a transparent background.

Bottom-left translucent bar, accent stripe on the left edge, name + title
right-aligned (Hebrew, shaped with python-bidi). --res 1080p or 4k (4k is
exactly 2x). Name/title/colors/font come from config.lower_third.

--apply overlays the PNG on final.mp4 for the first lower_third.show_seconds
seconds and writes final_lt.mp4 (a full re-encode).
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import Config, base_parser, die, require_file, require_tool  # noqa: E402

LAYOUT = {
    "1080p": {"W": 1920, "H": 1080, "bar": (80, 800, 720, 180), "radius": 14, "stripe": 8, "stripe_pad": 20,
              "name_size": 72, "title_size": 38, "pad_right": 30, "name_y": 30, "title_y": 110},
    "4k":    {"W": 3840, "H": 2160, "bar": (160, 1600, 1440, 360), "radius": 28, "stripe": 16, "stripe_pad": 40,
              "name_size": 144, "title_size": 76, "pad_right": 60, "name_y": 60, "title_y": 220},
}


def main() -> None:
    ap = base_parser(__doc__)
    ap.add_argument("--res", choices=list(LAYOUT), default="4k")
    ap.add_argument("--apply", action="store_true", help="overlay on final.mp4 -> final_lt.mp4")
    args = ap.parse_args()
    cfg = Config(args.config)
    try:
        from PIL import Image, ImageDraw, ImageFont
        from bidi.algorithm import get_display
    except ImportError:
        die("pip install Pillow python-bidi")

    lt = cfg.get("lower_third")
    if not lt.get("name"):
        print("config.lower_third.name is empty -> lower third skipped")
        return
    L = LAYOUT[args.res]
    W, H = L["W"], L["H"]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bx, by, bw, bh = L["bar"]
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=L["radius"], fill=tuple(lt["bar_color"]))
    d.rectangle([bx, by + L["stripe_pad"], bx + L["stripe"], by + bh - L["stripe_pad"]], fill=tuple(lt["accent_color"]))

    def font(size):
        candidates = [cfg.resolve(lt["font_path"])] if lt.get("font_path") else []
        candidates += ["/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for c in candidates:
            try:
                return ImageFont.truetype(c, size=size)
            except OSError:
                continue
        print("warning: no TrueType font found, using PIL default (Hebrew may not render)")
        return ImageFont.load_default()

    f_name, f_title = font(L["name_size"]), font(L["title_size"])
    name, title = get_display(lt["name"]), get_display(lt.get("title") or "")
    right = bx + bw - L["pad_right"]
    name_w = d.textlength(name, font=f_name)
    d.text((right - name_w, by + L["name_y"]), name, font=f_name, fill=tuple(lt["name_color"]))
    if title:
        title_w = d.textlength(title, font=f_title)
        d.text((right - title_w, by + L["title_y"]), title, font=f_title, fill=tuple(lt["title_color"]))

    P = cfg.paths()
    img.save(P["lower_third_png"])
    print(f"wrote {P['lower_third_png']} ({W}x{H})")

    if args.apply:
        require_tool("ffmpeg")
        final = require_file(P["final"], "11_concat.sh")
        out = cfg.out("final_lt.mp4")
        enc = cfg.get("encoder")
        secs = float(lt.get("show_seconds", 8))
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-stats", "-y",
               "-i", final, "-loop", "1", "-t", str(secs), "-i", P["lower_third_png"],
               "-filter_complex", f"[1:v]format=rgba[lt];[0:v][lt]overlay=x=0:y=0:enable='lt(t,{secs})'[v]",
               "-map", "[v]", "-map", "0:a",
               *cfg.video_codec_args(enc["body_bitrate"], enc["body_maxrate"], enc["body_bufsize"]),
               "-c:a", "copy", "-movflags", "+faststart", out]
        subprocess.run(cmd, check=True)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
