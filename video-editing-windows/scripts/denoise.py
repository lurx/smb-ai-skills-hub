# -*- coding: utf-8 -*-
# Cross-platform (Windows/Mac/Linux) background-noise cleanup: RNN denoise (arnndn) +
# low-rumble cut + loudness normalise, optionally burning ASS captions.
# usage: python denoise.py SRC OUT [ASS]     env FFMPEG (auto-detected otherwise)
# Windows note: ffmpeg filtergraphs choke on "C:\..." paths (drive colon), so we copy the
# RNN model (and font) next to the output and run ffmpeg from there, referencing by basename.
import sys, os, subprocess, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ffbin import ff_bin

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = ff_bin()
MODEL = os.path.join(SKILL, "models", "bd.rnnn")
FONT = os.path.join(SKILL, "fonts", "Arial Bold.ttf")

SRC = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
ASS = sys.argv[3] if len(sys.argv) > 3 else None

# work dir = where the filtergraph-referenced files must live (basenames, no drive colon)
workdir = os.path.dirname(os.path.abspath(ASS)) if ASS else os.path.dirname(OUT)
workdir = workdir or "."
shutil.copy(MODEL, os.path.join(workdir, "bd.rnnn"))

AUD = ("aformat=channel_layouts=mono,highpass=f=80,"
       "arnndn=m=bd.rnnn:mix=0.9,"
       "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,"
       "aformat=sample_fmts=fltp:channel_layouts=stereo")

if ASS:
    ass_name = os.path.basename(os.path.abspath(ASS))
    try:
        shutil.copy(FONT, os.path.join(workdir, "Arial Bold.ttf"))
    except Exception:
        pass
    fc = ("[0:v]setsar=1,fps=30,subtitles=" + ass_name + ":fontsdir=.,format=yuv420p[v];"
          "[0:a]" + AUD + "[a]")
    cmd = [FF, "-y", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT, "-loglevel", "error"]
else:
    cmd = [FF, "-y", "-i", SRC, "-af", AUD, "-c:v", "copy",
           "-c:a", "aac", "-b:a", "160k", OUT, "-loglevel", "error"]

subprocess.run(cmd, cwd=workdir, check=True)
print("denoised ->", OUT)
# mix=0.9 is a strong-but-natural clean. Lower to ~0.8 for gentler, raise toward 1.0 for max.
