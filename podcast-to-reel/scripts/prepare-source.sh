#!/usr/bin/env bash
# Crop one speaker's tile out of a podcast master and scale it to the card size.
#
#   ./prepare-source.sh <master> <out.mp4> <start-sec> <duration-sec> <crop> <scale>
#
# Example, using numbers from detect-layout.py:
#   ./prepare-source.sh master.mp4 public/source-05.mp4 3151.8 51.6 \
#        crop=634:342:646:180 1080:582
#
# Cut from the MASTER, never from a pre-made clip: existing clips often end
# mid-word. Always take a second of margin at each end so the reel config can
# place its own cut inside real silence.
set -euo pipefail

MASTER="${1:?see header}"; OUT="${2:?}"; START="${3:?}"; DUR="${4:?}"
CROP="${5:?}"; SCALE="${6:?}"

FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())' 2>/dev/null || command -v ffmpeg)"
[ -n "$FF" ] || { echo "ffmpeg not found: pip3 install --user imageio-ffmpeg" >&2; exit 1; }

mkdir -p "$(dirname "$OUT")"

# Output height must be even or libx264 rejects it under yuv420p.
"$FF" -y -ss "$START" -t "$DUR" -i "$MASTER" \
  -vf "${CROP},scale=${SCALE}:flags=lanczos" \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  "$OUT"

echo "wrote $OUT  (master ${START}s +${DUR}s)"
