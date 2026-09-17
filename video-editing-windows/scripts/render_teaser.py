# -*- coding: utf-8 -*-
# Cross-platform TEASER (podcast-style): fixed vertical crop from a 1920x1080 source, burn
# ASS captions, then a 5s branded end-card with music that ENDS exactly at the video end
# (quiet music intro builds under the clip tail, beat lands on the end-card).
# Use crop_render.py instead when the subject MOVES (needs face tracking).
# usage: python render_teaser.py SRC START DUR CROP_X ASS ENDCARD_IMG MUSIC SND_LEN OUT [CENSOR_EXPR]
#   CROP_X  = left x of a 608x1080 crop from a 1920x1080 source (tune so face is centred)
#   SND_LEN = seconds of music before its trailing silence (e.g. 13.69)
# env FFMPEG (auto-detected otherwise). Font is copied next to the ASS so ffmpeg needs no
# absolute path in the filtergraph (Windows drive-colon safe).
import sys, os, subprocess, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _ffbin import ff_bin

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = ff_bin()
FONT = os.path.join(SKILL, "fonts", "Arial Bold.ttf")

SRC = os.path.abspath(sys.argv[1])
START = sys.argv[2]
DUR = float(sys.argv[3])
CROPX = sys.argv[4]
ASS = sys.argv[5]
IMG = os.path.abspath(sys.argv[6])
MUSIC = os.path.abspath(sys.argv[7])
SND = float(sys.argv[8])
OUT = os.path.abspath(sys.argv[9])
CE = sys.argv[10] if len(sys.argv) > 10 else ""

ENDDUR = 5
DELAY = int((DUR + ENDDUR - SND) * 1000)
TOTAL = round(DUR + ENDDUR, 2)

workdir = os.path.dirname(os.path.abspath(ASS)) or "."
ass_name = os.path.basename(os.path.abspath(ASS))
try:
    shutil.copy(FONT, os.path.join(workdir, "Arial Bold.ttf"))
except Exception:
    pass

VID = ("[0:v]setpts=PTS-STARTPTS,crop=608:1080:" + CROPX + ":0,scale=1080:1920,setsar=1,fps=30,"
       "subtitles=" + ass_name + ":fontsdir=.,format=yuv420p[cv];"
       "[1:v]scale=1080:1080,pad=1080:1920:0:420:color=black,setsar=1,fps=30,format=yuv420p[ev];"
       "[cv][ev]concat=n=2:v=1:a=0[outv]")
MUS = (f"[2:a]atrim=0:{SND},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,"
       f"afade=t=out:st={SND - 0.4}:d=0.4,aresample=48000,"
       f"aformat=sample_fmts=fltp:channel_layouts=stereo,adelay={DELAY}|{DELAY}[music]")

if CE:
    fc = (VID + ";"
          f"[0:a]asetpts=PTS-STARTPTS,volume=volume='if({CE},0,1)':eval=frame,aresample=48000,"
          "aformat=sample_fmts=fltp:channel_layouts=stereo[voice];" + MUS + ";"
          f"[3:a]volume=volume='if({CE},0.33,0)':eval=frame,"
          "aformat=sample_fmts=fltp:channel_layouts=stereo[beep];"
          "[voice][beep][music]amix=inputs=3:duration=longest:normalize=0[outa]")
    inputs = ["-ss", START, "-t", str(DUR), "-i", SRC,
              "-loop", "1", "-framerate", "30", "-t", str(ENDDUR), "-i", IMG,
              "-i", MUSIC,
              "-f", "lavfi", "-t", str(DUR), "-i", "sine=frequency=1000:sample_rate=48000"]
else:
    fc = (VID + ";"
          "[0:a]asetpts=PTS-STARTPTS,aresample=48000,"
          "aformat=sample_fmts=fltp:channel_layouts=stereo[voice];" + MUS + ";"
          "[voice][music]amix=inputs=2:duration=longest:normalize=0[outa]")
    inputs = ["-ss", START, "-t", str(DUR), "-i", SRC,
              "-loop", "1", "-framerate", "30", "-t", str(ENDDUR), "-i", IMG,
              "-i", MUSIC]

cmd = ([FF, "-y"] + inputs + ["-filter_complex", fc, "-map", "[outv]", "-map", "[outa]",
       "-t", str(TOTAL), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
       OUT, "-loglevel", "error"])
subprocess.run(cmd, cwd=workdir, check=True)
print("teaser ->", OUT)
