#!/usr/bin/env bash
# Stage 10: build intro.mp4 / outro.mp4 = configured mp3 over a black frame
# at the body's resolution. Durations come from ffprobe of the mp3.
# If intro_audio / outro_audio are empty in config, the stage is skipped
# gracefully and 11_concat.sh will produce final.mp4 from the body alone.
# Usage: bash 10_intro_outro.sh [--config config.json]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="./config.json"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
LIB="python3 $SCRIPT_DIR/lib_config.py --config $CONFIG"
command -v ffmpeg >/dev/null || { echo "ERROR: ffmpeg not found"; exit 1; }

BODY="$($LIB path body)"
[[ -f "$BODY" ]] || { echo "ERROR: missing $BODY (run 09_render_body.py first)"; exit 1; }
SIZE=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$BODY")
FPS="$($LIB get fps)"
CODEC="$($LIB get encoder.video_codec)"
VBR="$($LIB get encoder.intro_bitrate)"
ABR="$($LIB get encoder.audio_bitrate)"

build() {  # kind, key
  local KIND="$1" KEY="$2"
  local MP3; MP3="$($LIB get "$KEY" --resolve || true)"
  local OUT; OUT="$($LIB path "$KIND")"
  if [[ -z "$MP3" || "$MP3" == "$($LIB project_dir)" ]]; then
    echo "[$KIND] no $KEY in config -> skipped"; rm -f "$OUT"; return
  fi
  [[ -f "$MP3" ]] || { echo "ERROR: $KEY points to a missing file: $MP3"; exit 1; }
  local DUR; DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$MP3")
  echo "[$KIND] $MP3 (${DUR}s) -> $OUT @ ${SIZE}"
  ffmpeg -hide_banner -loglevel warning -stats -y \
    -f lavfi -t "$DUR" -i "color=c=black:s=${SIZE}:r=${FPS}" \
    -i "$MP3" \
    -c:v "$CODEC" -b:v "$VBR" -tag:v avc1 -pix_fmt yuv420p \
    -c:a aac -b:a "$ABR" -ar 48000 -ac 2 \
    -t "$DUR" "$OUT"
}
build intro intro_audio
build outro outro_audio
echo "done"
