#!/usr/bin/env bash
# Stage 05: 1080p H.264 proxies of each camera trimmed to the episode range,
# plus audio_track.m4a from the mic camera (the master audio for everything
# downstream: Whisper, correlation cuts, final render, reels).
# After this, both proxies start at t=0 and are time-aligned.
# Usage: bash 05_proxies.sh [--config config.json]
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

TRIM="$($LIB path trim)"; SYNCF="$($LIB path sync_offset)"
[[ -f "$TRIM" ]]  || { echo "ERROR: missing $TRIM (run 02_trim.py first)"; exit 1; }
[[ -f "$SYNCF" ]] || { echo "ERROR: missing $SYNCF (run 01_sync.py first)"; exit 1; }
read IN_MIC OUT_MIC < "$TRIM"
SYNC=$(cat "$SYNCF")                       # mic_t = other_t + sync
MIC="$($LIB get mic_cam)"
if [[ "$MIC" == "host" ]]; then OTHER=guest; else OTHER=host; fi

IN_OTHER=$(awk -v a="$IN_MIC" -v s="$SYNC" 'BEGIN{printf "%.3f", a - s}')
DUR=$(awk -v a="$OUT_MIC" -v b="$IN_MIC" 'BEGIN{printf "%.3f", a - b}')
echo "trim duration: ${DUR}s"
echo "$MIC trim in: ${IN_MIC}   $OTHER trim in: ${IN_OTHER}"

CODEC=(); while IFS= read -r l; do CODEC+=("$l"); done < <($LIB codec_args)   # bash 3.2 compatible
ABR="$($LIB get encoder.audio_bitrate)"

render_proxy() {  # role, in-point
  local ROLE="$1" IN="$2"
  local SRC; SRC="$($LIB campath "$ROLE")"
  local DST; DST="$($LIB path "proxy_$ROLE")"
  echo; echo "rendering $ROLE proxy -> $DST"
  ffmpeg -hide_banner -loglevel warning -stats -y \
    -ss "$IN" -i "$SRC" -t "$DUR" -an \
    -vf "scale=1920:1080:flags=fast_bilinear" \
    "${CODEC[@]}" -movflags +faststart "$DST"
}
render_proxy "$MIC" "$IN_MIC"
render_proxy "$OTHER" "$IN_OTHER"

AUDIO="$($LIB path audio_track)"
echo; echo "[audio] extracting $MIC audio -> $AUDIO"
ffmpeg -hide_banner -loglevel warning -stats -y \
  -ss "$IN_MIC" -i "$($LIB campath "$MIC")" -t "$DUR" -vn \
  -ac 2 -ar 48000 -c:a aac -b:a "$ABR" "$AUDIO"

ls -lh "$($LIB path proxy_host)" "$($LIB path proxy_guest)" "$AUDIO"
