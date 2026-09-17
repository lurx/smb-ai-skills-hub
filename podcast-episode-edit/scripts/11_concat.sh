#!/usr/bin/env bash
# Stage 11: concatenate intro + body + outro -> final.mp4 (re-encode via the
# concat filter, which is robust across differently-encoded inputs).
# Missing intro/outro (not configured) are simply left out.
# Usage: bash 11_concat.sh [--config config.json]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="./config.json"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
LIB="python3 $SCRIPT_DIR/lib_config.py --config $CONFIG"
command -v ffmpeg >/dev/null || { echo "ERROR: ffmpeg not found"; exit 1; }

BODY="$($LIB path body)"; INTRO="$($LIB path intro)"; OUTRO="$($LIB path outro)"; FINAL="$($LIB path final)"
[[ -f "$BODY" ]] || { echo "ERROR: missing $BODY (run 09_render_body.py first)"; exit 1; }

INPUTS=(); N=0; FC=""
for F in "$INTRO" "$BODY" "$OUTRO"; do
  if [[ -f "$F" ]]; then INPUTS+=(-i "$F"); FC+="[$N:v][$N:a]"; N=$((N+1)); else echo "skipping (not built): $F"; fi
done

CODEC="$($LIB get encoder.video_codec)"
VBR="$($LIB get encoder.body_bitrate)"; MAXR="$($LIB get encoder.body_maxrate)"; BUFS="$($LIB get encoder.body_bufsize)"
ABR="$($LIB get encoder.audio_bitrate)"
EXTRA=(); [[ "$CODEC" == "libx264" ]] && EXTRA=(-preset "$($LIB get encoder.x264_preset)")

echo "concatenating $N parts -> $FINAL"
ffmpeg -hide_banner -loglevel warning -stats -y "${INPUTS[@]}" \
  -filter_complex "${FC}concat=n=${N}:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  -c:v "$CODEC" -b:v "$VBR" -maxrate "$MAXR" -bufsize "$BUFS" ${EXTRA[@]+"${EXTRA[@]}"} \
  -tag:v avc1 -pix_fmt yuv420p \
  -c:a aac -b:a "$ABR" -movflags +faststart "$FINAL"
ls -lh "$FINAL"
echo "DONE -> $FINAL"
