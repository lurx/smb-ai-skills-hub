#!/usr/bin/env python3
"""Stage 07: map the Whisper transcript onto the segments where the
REELS camera (config reels_cam, default guest) is on screen, and dump the
text per block with timestamps. Read guest_text.txt, pick the strongest
moments, and write them into hooks.json (see hooks.example.json).

Whisper timestamps are on audio_track.m4a = sequence time, so they compare
directly with cuts.json segment times.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import Config, base_parser, load_json, require_file, save_json  # noqa: E402


def main() -> None:
    ap = base_parser(__doc__)
    ap.add_argument("--cuts", choices=["base", "final"], default="base",
                    help="which cuts file to use for camera ownership (default base)")
    args = ap.parse_args()
    cfg = Config(args.config)
    P = cfg.paths()
    cuts_path = P["cuts"] if args.cuts == "base" else P["cuts_final"]
    doc = load_json(require_file(cuts_path, "04_cuts_base.py" if args.cuts == "base" else "08_cuts_audio_correlation.py"))
    cam = cfg.reels_cam
    segs = [s for s in doc["segments"] if s["cam"] == cam]
    print(f"{cam}-only segments: {len(segs)}, total {sum(s['duration'] for s in segs):.1f}s")

    w = load_json(require_file(P["whisper"], "06_transcribe.py"))
    words = w.get("words") or []
    print(f"whisper words: {len(words)}, segments: {len(w.get('segments') or [])}")

    blocks = []
    wi = 0
    for seg in segs:
        t0, t1 = seg["t0"], seg["t1"]
        block_words = []
        while wi < len(words) and words[wi]["end"] <= t0:
            wi += 1
        j = wi
        while j < len(words) and words[j]["start"] < t1:
            block_words.append(words[j])
            j += 1
        if block_words:
            blocks.append({"t0": t0, "t1": t1, "duration": round(t1 - t0, 2),
                           "text": " ".join(x["word"] for x in block_words).strip(),
                           "words": block_words})
    print(f"\n{cam} blocks with text: {len(blocks)}")

    save_json(P["guest_blocks"], blocks)
    with open(P["guest_text"], "w", encoding="utf-8") as f:
        for b in blocks:
            m0, s0 = divmod(int(b["t0"]), 60)
            m1, s1 = divmod(int(b["t1"]), 60)
            f.write(f"[{m0:02d}:{s0:02d}-{m1:02d}:{s1:02d}] ({b['duration']:.1f}s) {b['text']}\n")
    print(f"wrote {P['guest_blocks']} and {P['guest_text']}")
    print("\nNEXT: read guest_text.txt, pick 5-10 self-contained moments (15-50s each)\n"
          f"      and write them to {P['hooks']} as [{{\"slug\", \"start\", \"end\"}}].\n"
          "      Times are sequence seconds (same as the brackets above).\n"
          "      Then run 08_cuts_audio_correlation.py -> 09_render_body.py.")


if __name__ == "__main__":
    main()
