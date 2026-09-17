# -*- coding: utf-8 -*-
# Cross-platform one-time setup (Windows / macOS / Linux).
# Installs the Python deps that are NOT bundled and resolves a cross-platform ffmpeg.
# Bundled models + font are verified. usage: python scripts/setup.py
import sys, os, subprocess, importlib

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def have(mod):
    try:
        importlib.import_module(mod)
        return True
    except Exception:
        return False


print("skill: ", SKILL)
print("python:", sys.executable)

# 1) pip deps: faster-whisper (transcription), opencv + pillow (tracking/captions),
#    imageio-ffmpeg (bundled cross-platform ffmpeg binary — no system install needed)
need = []
if not have("faster_whisper"):
    need.append("faster-whisper")
if not have("cv2"):
    need.append("opencv-python")
if not have("PIL"):
    need.append("pillow")
if not have("imageio_ffmpeg"):
    need.append("imageio-ffmpeg")
if need:
    print("installing:", ", ".join(need), "...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", "pip"], check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", *need], check=False)
else:
    print("all python deps already present")

# 2) resolve a bundled, cross-platform ffmpeg
ffmpeg = None
try:
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
except Exception as e:
    print("WARN could not resolve bundled ffmpeg:", e)

# 3) verify bundled assets
print()
for f in ["models/MobileNetSSD_deploy.caffemodel", "models/yunet.onnx",
          "models/bd.rnnn", "fonts/Arial Bold.ttf"]:
    print(("  ok       " if os.path.exists(os.path.join(SKILL, f)) else "  MISSING  ") + f)

print()
print("READY.")
if ffmpeg:
    print("FFMPEG =", ffmpeg)
print("PY     =", sys.executable)
print()
print("The render scripts auto-detect ffmpeg, so no env var is required.")
print("To pin a specific ffmpeg, set FFMPEG first:")
if os.name == "nt":
    ff_hint = ffmpeg or "C:\\path\\to\\ffmpeg.exe"
    print('  set "FFMPEG=' + ff_hint + '"')
else:
    ff_hint = ffmpeg or "/path/to/ffmpeg"
    print('  export FFMPEG="' + ff_hint + '"')
