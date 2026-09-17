# -*- coding: utf-8 -*-
# Cross-platform multi-cam clip render to a 9:16 reel: per-shot static crop centered on the
# active speaker (snaps at cuts), burn captions, keep audio.
# usage: render_clip.py SRC START DUR PLAN.json ASS FONTSDIR OUT [FACE_MULT]
#   FONTSDIR is accepted for compatibility but the bundled font is used and copied next to
#   the ASS, then referenced by basename with fontsdir=. (Windows drive-colon safe).
import sys, json, subprocess, os, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ffbin import ff_bin

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = ff_bin()
FONT = os.path.join(SK, "fonts", "Arial Bold.ttf")

src = os.path.abspath(sys.argv[1]); start = float(sys.argv[2]); dur = float(sys.argv[3])
plan = json.load(open(sys.argv[4])); ass = sys.argv[5]; out = os.path.abspath(sys.argv[7])
FACE_MULT = float(sys.argv[8]) if len(sys.argv) > 8 else 4.2

SW, SH = plan["SW"], plan["SH"]
OUT_W, OUT_H = 1080, 1920
maxCW = min(SW, (SH * OUT_W) // OUT_H)          # widest crop that fits 9:16 in the source height
CW = int(round(plan["face_h_med"] * FACE_MULT))
CW = max(900, min(CW, maxCW))
CW -= CW % 2
CH = int(round(CW * OUT_H / OUT_W)); CH = min(CH, SH); CH -= CH % 2

def clampx(cx): return int(max(0, min(cx - CW / 2, SW - CW)))
def clampy(cy): return int(max(0, min(cy - CH * 0.40, SH - CH)))   # eyes ~upper third

shots = plan["shots"]
shots = [s for s in shots if s["t1"] > 0 and s["t0"] < dur]
if shots:
    shots[0]["t0"] = 0.0
    shots[-1]["t1"] = round(dur, 3)

parts = []; labels = []
for i, s in enumerate(shots):
    x0 = clampx(s["cx"]); y0 = clampy(s["cy"])
    parts.append(
        f"[0:v]trim={s['t0']:.3f}:{s['t1']:.3f},setpts=PTS-STARTPTS,"
        f"crop={CW}:{CH}:{x0}:{y0},scale={OUT_W}:{OUT_H}:flags=lanczos,setsar=1[v{i}]")
    labels.append(f"[v{i}]")
concat = "".join(labels) + f"concat=n={len(labels)}:v=1:a=0[vc]"
tail = [concat]

# Windows-safe subtitle path: run ffmpeg from the ASS dir, reference by basename.
if ass and ass != "-":
    ass_abs = os.path.abspath(ass)
    workdir = os.path.dirname(ass_abs) or "."
    ass_name = os.path.basename(ass_abs)
    try:
        shutil.copy(FONT, os.path.join(workdir, "Arial Bold.ttf"))
    except Exception:
        pass
    tail.append("[vc]subtitles=filename=" + ass_name + ":fontsdir=.[vout]")
    vlabel = "[vout]"
else:
    workdir = os.path.dirname(out) or "."
    vlabel = "[vc]"
fc = ";".join(parts + tail)

cmd = [FF, "-y", "-ss", str(start), "-t", str(dur), "-i", src,
       "-filter_complex", fc,
       "-map", vlabel, "-map", "0:a",
       "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
print(f"CW={CW} CH={CH} shots={len(shots)}", flush=True)
r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, cwd=workdir)
if r.returncode != 0:
    sys.stderr.write(r.stderr.decode("utf-8", "replace")[-3000:]); sys.exit(1)
print("done", out)
