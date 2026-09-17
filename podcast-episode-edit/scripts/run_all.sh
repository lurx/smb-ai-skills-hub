#!/usr/bin/env bash
# Orchestrator: run the pipeline stages in order.
# Usage: bash run_all.sh [--config config.json] [--from N] [--to N] [--no-subs]
#   --from N   start at stage N (0-14); earlier outputs must already exist
#   --to N     stop after stage N
# Stage 07 stops the pipeline on its first run if hooks.json does not exist
# yet: read guest_text.txt, write hooks.json, then rerun with --from 8.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="./config.json"; FROM=0; TO=14; SUBS="--subs"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --from) FROM="$2"; shift 2 ;;
    --to) TO="$2"; shift 2 ;;
    --no-subs) SUBS="--no-subs"; shift ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
CONFIG="$(cd "$(dirname "$CONFIG")" && pwd)/$(basename "$CONFIG")"
[[ -f "$CONFIG" ]] || { echo "ERROR: $CONFIG not found (copy config.example.json -> config.json)"; exit 1; }
HOOKS="$(python3 "$SCRIPT_DIR/lib_config.py" --config "$CONFIG" path hooks)"

stage() {  # N, description, command...
  local N="$1" DESC="$2"; shift 2
  (( N < FROM || N > TO )) && return 0
  echo; echo "=============== stage $N: $DESC"; echo
  "$@"
}
py() { python3 "$SCRIPT_DIR/$1" --config "$CONFIG" "${@:2}"; }
sh_() { bash "$SCRIPT_DIR/$1" --config "$CONFIG" "${@:2}"; }

stage 0  "extract 8kHz audio"            sh_ 00_extract_audio.sh
stage 1  "sync cameras"                  py  01_sync.py
stage 2  "trim (voice activity)"         py  02_trim.py
stage 3  "face motion signals"           py  03_motion.py
stage 4  "baseline cuts"                 py  04_cuts_base.py
stage 5  "proxies + audio track"         sh_ 05_proxies.sh
stage 6  "whisper transcription"         py  06_transcribe.py --from-json
stage 7  "guest text for hook picking"   py  07_find_hooks.py
if (( FROM <= 7 && TO >= 8 )) && [[ ! -f "$HOOKS" ]]; then
  echo; echo "STOP: write $HOOKS (see hooks.example.json), then: bash run_all.sh --config $CONFIG --from 8"
  exit 0
fi
stage 8  "audio-correlation cuts"        py  08_cuts_audio_correlation.py
stage 9  "render body"                   py  09_render_body.py
stage 10 "intro/outro"                   sh_ 10_intro_outro.sh
stage 11 "concat final"                  sh_ 11_concat.sh
stage 12 "reels"                         py  12_render_reels.py "$SUBS"
stage 13 "lower third PNG"               py  13_lower_thirds.py
stage 14 "full episode captions (.ass)"  py  14_full_subs.py
echo; echo "pipeline finished."
