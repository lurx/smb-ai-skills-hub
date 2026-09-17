#!/usr/bin/env python3
"""Stage 06: transcribe audio_track.m4a with OpenAI Whisper (word timestamps).

The audio is split into N-second mp3 chunks (config whisper.chunk_seconds,
default 600 = under the 25 MB upload limit), each chunk is sent to the
whisper-1 API as verbose_json with word + segment granularity, and the
per-chunk results are merged with a time offset of chunk_index * chunk_seconds
into one whisper.json on the sequence timeline.

Requires OPENAI_API_KEY in the environment (never stored in config).
Chunk JSONs are cached in work/chunks/, so a rerun only transcribes what
is missing. Use --from-json to skip everything when whisper.json exists.
"""
import glob
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_config import (Config, base_parser, die, ffprobe_duration,  # noqa: E402
                        load_json, require_file, require_tool, save_json)


def split_audio(audio: str, chunks_dir: str, chunk_seconds: int) -> list:
    os.makedirs(chunks_dir, exist_ok=True)
    total = ffprobe_duration(audio)
    n = int(total // chunk_seconds) + (1 if total % chunk_seconds > 0.5 else 0)
    paths = []
    for i in range(n):
        out = os.path.join(chunks_dir, f"chunk_{i:02d}.mp3")
        paths.append(out)
        if os.path.isfile(out):
            continue
        print(f"  splitting chunk {i+1}/{n} -> {out}")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-ss", str(i * chunk_seconds), "-t", str(chunk_seconds),
                        "-i", audio, "-vn", "-ac", "1", "-ar", "16000",
                        "-c:a", "libmp3lame", "-b:a", "64k", out], check=True)
    return paths


def transcribe_chunk(client, mp3: str, model: str, language: str) -> dict:
    with open(mp3, "rb") as f:
        res = client.audio.transcriptions.create(
            model=model, file=f, response_format="verbose_json",
            timestamp_granularities=["word", "segment"], language=language)
    return res.model_dump() if hasattr(res, "model_dump") else dict(res)


def merge_chunks(chunks_dir: str, chunk_seconds: float) -> dict:
    merged = {"text": "", "segments": [], "words": []}
    for i, p in enumerate(sorted(glob.glob(os.path.join(chunks_dir, "chunk_*.json")))):
        offset = i * chunk_seconds
        d = load_json(p)
        merged["text"] += (" " if merged["text"] else "") + (d.get("text") or "")
        for s in d.get("segments") or []:
            s2 = dict(s); s2["start"] = s2.get("start", 0) + offset; s2["end"] = s2.get("end", 0) + offset
            merged["segments"].append(s2)
        for w in d.get("words") or []:
            w2 = dict(w); w2["start"] = w2.get("start", 0) + offset; w2["end"] = w2.get("end", 0) + offset
            merged["words"].append(w2)
    return merged


def main() -> None:
    ap = base_parser(__doc__)
    ap.add_argument("--from-json", action="store_true",
                    help="skip transcription if whisper.json already exists")
    args = ap.parse_args()
    cfg = Config(args.config)
    P = cfg.paths()

    if args.from_json and os.path.isfile(P["whisper"]):
        d = load_json(P["whisper"])
        print(f"whisper.json exists: {len(d.get('segments', []))} segments, {len(d.get('words', []))} words. skipping.")
        return

    require_tool("ffmpeg")
    audio = require_file(P["audio_track"], "05_proxies.sh")
    if not os.environ.get("OPENAI_API_KEY"):
        die("OPENAI_API_KEY is not set. export OPENAI_API_KEY=sk-... and rerun")
    try:
        from openai import OpenAI
    except ImportError:
        die("openai package missing: pip install openai")

    chunk_seconds = int(cfg.get("whisper.chunk_seconds"))
    model = cfg.get("whisper.model")
    language = cfg.get("whisper.language")
    print(f"splitting {audio} into {chunk_seconds}s chunks ...")
    mp3s = split_audio(audio, P["chunks_dir"], chunk_seconds)

    client = OpenAI()
    for i, mp3 in enumerate(mp3s):
        jpath = mp3[:-4] + ".json"
        if os.path.isfile(jpath):
            print(f"  chunk {i+1}/{len(mp3s)}: cached")
            continue
        print(f"  chunk {i+1}/{len(mp3s)}: uploading + transcribing ...")
        t0 = time.time()
        data = transcribe_chunk(client, mp3, model, language)
        save_json(jpath, data)
        print(f"    done in {time.time()-t0:.1f}s  ({len(data.get('words') or [])} words)")

    merged = merge_chunks(P["chunks_dir"], float(chunk_seconds))
    save_json(P["whisper"], merged)
    print(f"\nmerged {len(mp3s)} chunks -> {P['whisper']}")
    print(f"segments: {len(merged['segments'])}, words: {len(merged['words'])}")
    for s in merged["segments"][:5]:
        print(f"  [{s['start']:6.2f}-{s['end']:6.2f}]  {s['text'].strip()[:70]}")


if __name__ == "__main__":
    main()
