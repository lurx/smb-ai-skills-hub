#!/bin/bash
# One-time setup for the video-editing skill. Installs the runtime deps that are NOT
# bundled (they are big / platform-specific) and verifies the bundled models/font.
# Prints FFMPEG and PY paths to use. Run once per session/work dir.
#   usage: source scripts/setup.sh   (or: bash scripts/setup.sh then export the vars it prints)
set -e
SKILL="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
WORK="${1:-$PWD/.videowork}"; mkdir -p "$WORK/bin"
echo "skill: $SKILL"; echo "work:  $WORK"

# 1) ffmpeg + ffprobe (static, via npm — no system install, works on macOS arm64)
if [ ! -x "$WORK/node_modules/ffmpeg-static/ffmpeg" ]; then
  # npm init -y fails when the dir name is an invalid package name (dot-prefixed, Hebrew) — write package.json directly
  ( cd "$WORK" && { [ -f package.json ] || echo '{"name":"videowork","version":"1.0.0","private":true}' > package.json; } && npm install ffmpeg-static ffprobe-static >/dev/null 2>&1 )
fi
ln -sf "$WORK/node_modules/ffmpeg-static/ffmpeg" "$WORK/bin/ffmpeg"
ln -sf "$WORK/node_modules/ffprobe-static/bin/darwin/arm64/ffprobe" "$WORK/bin/ffprobe"

# 2) python deps (mlx-whisper for Apple Silicon transcription; opencv+pillow for tracking/captions)
if [ ! -x "$WORK/venv/bin/python" ]; then python3 -m venv "$WORK/venv"; fi
"$WORK/venv/bin/python" -m pip install --quiet --upgrade pip >/dev/null 2>&1 || true
"$WORK/venv/bin/python" -c "import mlx_whisper" 2>/dev/null || "$WORK/venv/bin/python" -m pip install --quiet mlx-whisper
"$WORK/venv/bin/python" -c "import cv2" 2>/dev/null       || "$WORK/venv/bin/python" -m pip install --quiet opencv-python
"$WORK/venv/bin/python" -c "import PIL" 2>/dev/null       || "$WORK/venv/bin/python" -m pip install --quiet pillow

# 3) verify bundled assets
for f in models/MobileNetSSD_deploy.caffemodel models/yunet.onnx models/bd.rnnn "fonts/Arial Bold.ttf"; do
  [ -e "$SKILL/$f" ] && echo "  ok $f" || echo "  MISSING $f"
done
export FFMPEG="$WORK/bin/ffmpeg"; export FFPROBE="$WORK/bin/ffprobe"; export PY="$WORK/venv/bin/python"; export PATH="$WORK/bin:$PATH"
echo ""
echo "READY. Use:  FFMPEG=$FFMPEG   PY=$PY"
echo "(export FFMPEG so crop_render.py picks it up, and call scripts with \$PY)"
