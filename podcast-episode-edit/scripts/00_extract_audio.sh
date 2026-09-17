#!/usr/bin/env bash
# Stage 00: extract 8 kHz mono PCM audio from each camera.
# Used by 01_sync (cross-correlation) and 02_trim (voice activity).
# Usage: bash 00_extract_audio.sh [--config config.json]
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

for ROLE in host guest; do
  SRC="$($LIB campath "$ROLE")"
  DST="$($LIB path "pcm_$ROLE")"
  echo "[$ROLE] $SRC -> $DST (8kHz mono s16le)"
  ffmpeg -hide_banner -loglevel error -stats -y \
    -i "$SRC" -vn -ac 1 -ar 8000 -f s16le -acodec pcm_s16le "$DST"
done
echo "done: audio extracted for both cameras"
