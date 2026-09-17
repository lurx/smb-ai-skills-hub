# -*- coding: utf-8 -*-
# Cross-platform Hebrew word-level transcription with faster-whisper (Windows/Mac/Linux).
# Feed a WAV/MP4/MOV. usage: python transcribe.py AUDIO_OR_VIDEO OUT.json [words|segments]
#   words    -> [{"s","e","w"}]                     (for karaoke captions)
#   segments -> [{"start","end","text"}] + prints [mm:ss] text (for picking moments)
# env WHISPER_MODEL (default "large-v3"); first run downloads the CT2 model from HuggingFace.
# All JSON is written UTF-8 (critical on Windows, whose default encoding mangles Hebrew).
import sys, json, os
from faster_whisper import WhisperModel

src = sys.argv[1]
out = sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else "words"

model_name = os.environ.get("WHISPER_MODEL", "large-v3")
# int8 runs on any CPU with low memory; device="auto" uses CUDA when present.
model = WhisperModel(model_name, device="auto", compute_type="int8")
segments, info = model.transcribe(
    src, language="he", word_timestamps=(mode == "words"),
    condition_on_previous_text=False, vad_filter=True)
segments = list(segments)

if mode == "words":
    w = [{"s": round(wd.start, 2), "e": round(wd.end, 2), "w": wd.word.strip()}
         for s in segments for wd in (s.words or [])]
    json.dump(w, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(len(w), "words")
else:
    segs = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
            for s in segments]
    json.dump(segs, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    def f(t):
        return f"{int(t // 60):02d}:{int(t % 60):02d}"
    for s in segs:
        if s["text"]:
            print(f"[{f(s['start'])}] {s['text']}")
# NOTE: whisper can hallucinate on a hard/long stretch. Fix by re-transcribing THAT window
# in ~10s chunks (chunking breaks the loop). Always scan tokens for stray Latin letters.
