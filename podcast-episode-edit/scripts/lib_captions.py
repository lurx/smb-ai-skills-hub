#!/usr/bin/env python3
"""Shared caption module (ASS subtitles from Whisper word timestamps).

Pipeline for any caption job:
    words (Whisper, local time)  ->  preprocess_words()  ->  group_words()  ->  make_ass()

Why fixes are applied to the WORD STREAM before grouping: a misheard word
that spans two caption groups can only be fixed reliably while the words
are still one continuous list. Phrase fixes (multi-word) are applied a
second time on the final group text as a safety net.

fixes.json format (all keys optional):
{
  "word_fixes":         {"wrong": "right"},          whole-token replacement
  "prefix_aware_fixes": {"wrong": "right"},          substring replacement (catches ה/ל/ש prefixes)
  "percent_followers":  ["מהאנשים", "מהם"],           number + one of these => "NN%"
  "phrase_fixes":       [["wrong phrase", "right phrase"]]
}
"""
import json
import os
import re
from typing import Any, Dict, List, Optional

# ---- resolution presets (font/margins tuned per canvas) -------------------
PRESETS: Dict[str, Dict[str, Any]] = {
    # 9:16 reels: big 2-word groups, low on the frame but above UI chrome
    "reel": {
        "play_x": 1080, "play_y": 1920,
        "font_size": 150, "outline": 12,
        "margin_l": 60, "margin_r": 60, "margin_v": 380,
        "max_per_group": 2, "max_pause": 0.4, "max_chars": 14,
    },
    # 16:9 1080p full episode
    "1080p": {
        "play_x": 1920, "play_y": 1080,
        "font_size": 60, "outline": 5,
        "margin_l": 80, "margin_r": 80, "margin_v": 80,
        "max_per_group": 3, "max_pause": 0.6, "max_chars": 18,
    },
    # 16:9 4K: exactly 2x the 1080p layout
    "4k": {
        "play_x": 3840, "play_y": 2160,
        "font_size": 120, "outline": 10,
        "margin_l": 160, "margin_r": 160, "margin_v": 160,
        "max_per_group": 3, "max_pause": 0.6, "max_chars": 18,
    },
}


# ---- fixes --------------------------------------------------------------
class Fixes:
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        data = data or {}
        self.word_fixes: Dict[str, str] = dict(data.get("word_fixes") or {})
        self.prefix_aware: Dict[str, str] = dict(data.get("prefix_aware_fixes") or {})
        self.percent_followers = set(data.get("percent_followers") or [])
        self.phrase_fixes: List[List[str]] = [list(p) for p in (data.get("phrase_fixes") or [])]

    @classmethod
    def load(cls, path: Optional[str]) -> "Fixes":
        if path and os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                return cls(json.load(f))
        return cls()

    def fix_text(self, s: str) -> str:
        for old, new in self.phrase_fixes:
            s = s.replace(old, new)
        return s


# ---- word stream preprocessing -----------------------------------------
def preprocess_words(words: List[Dict[str, Any]], fixes: Optional[Fixes] = None) -> List[Dict[str, Any]]:
    """Apply per-word fixes and merge compound patterns into single tokens.

    Merges:
      ה + number            -> "ה-NN"
      מ/ל + English word    -> "מ-Word"
      number + %-follower   -> "NN%"        (follower word kept as its own token)
      number + הם + follower-> "NN%"
    """
    fixes = fixes or Fixes()
    words = [w for w in words if str(w.get("word", "")).strip()]
    cleaned = []
    for w in words:
        token = w["word"].strip()
        if token in fixes.word_fixes:
            token = fixes.word_fixes[token]
        for src, dst in fixes.prefix_aware.items():
            if src in token and src != token:
                token = token.replace(src, dst)
        cleaned.append({**w, "word": token})

    merged: List[Dict[str, Any]] = []
    i = 0
    n = len(cleaned)
    while i < n:
        w = cleaned[i]
        nxt = cleaned[i + 1] if i + 1 < n else None
        token = w["word"]
        if nxt and token == "ה" and re.fullmatch(r"\d+", nxt["word"]):
            merged.append({**w, "word": f"ה-{nxt['word']}", "end": nxt["end"]})
            i += 2
            continue
        if nxt and token in {"מ", "ל"} and re.fullmatch(r"[A-Z][A-Za-z0-9]*", nxt["word"]):
            merged.append({**w, "word": f"{token}-{nxt['word']}", "end": nxt["end"]})
            i += 2
            continue
        if nxt and re.fullmatch(r"\d+", token) and nxt["word"] in fixes.percent_followers:
            merged.append({**w, "word": f"{token}%"})
            i += 1
            continue
        if (nxt and i + 2 < n and re.fullmatch(r"\d+", token)
                and nxt["word"] == "הם" and cleaned[i + 2]["word"] in fixes.percent_followers):
            merged.append({**w, "word": f"{token}%"})
            i += 1
            continue
        merged.append(w)
        i += 1
    return merged


# ---- grouping -----------------------------------------------------------
def group_words(words: List[Dict[str, Any]], max_per_group: int = 2,
                max_pause: float = 0.4, max_chars: int = 14) -> List[List[Dict[str, Any]]]:
    """Greedy grouping: start a new caption when the group is full, the
    pause before this word is long, or the text would get too wide."""
    groups: List[List[Dict[str, Any]]] = []
    cur: List[Dict[str, Any]] = []
    for w in words:
        if not cur:
            cur = [w]
            continue
        gap = w["start"] - cur[-1]["end"]
        new_text = " ".join(x["word"] for x in cur + [w])
        if len(cur) >= max_per_group or gap > max_pause or len(new_text) > max_chars:
            groups.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        groups.append(cur)
    return groups


def group_for_preset(words: List[Dict[str, Any]], preset: str) -> List[List[Dict[str, Any]]]:
    p = PRESETS[preset]
    return group_words(words, p["max_per_group"], p["max_pause"], p["max_chars"])


# ---- ASS output ---------------------------------------------------------
def t_to_ass(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - 60 * m - 3600 * h
    return f"{h}:{m:02d}:{s:05.2f}"


def make_ass(groups: List[List[Dict[str, Any]]], total_dur: float, preset: str = "reel",
             font_name: str = "Secular One", fixes: Optional[Fixes] = None) -> str:
    """Build a complete .ass document. Each caption shows from slightly
    before its first word until just before the next group starts."""
    if preset not in PRESETS:
        raise ValueError(f"unknown preset {preset!r}; choose from {sorted(PRESETS)}")
    p = PRESETS[preset]
    fixes = fixes or Fixes()
    style = (
        f"Style: Default,{font_name},{p['font_size']},"
        "&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
        "1,0,0,0,100,100,0,0,1,"
        f"{p['outline']},0,2,{p['margin_l']},{p['margin_r']},{p['margin_v']},1"
    )
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {p['play_x']}
PlayResY: {p['play_y']}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for i, g in enumerate(groups):
        start = max(0.0, g[0]["start"] - 0.05)
        if i + 1 < len(groups):
            end = groups[i + 1][0]["start"] - 0.02
        else:
            end = min(g[-1]["end"] + 0.6, total_dur)
        end = max(end, start + 0.25)
        text = " ".join(w["word"].strip() for w in g)
        text = fixes.fix_text(" " + text + " ").strip()
        events.append(f"Dialogue: 0,{t_to_ass(start)},{t_to_ass(end)},Default,,0,0,0,,{text}")
    return head + "\n".join(events) + "\n"


def words_in_ranges(all_words: List[Dict[str, Any]], ranges: List[List[float]]) -> List[Dict[str, Any]]:
    """Re-base words from sequence time into the local time of a clip made
    by concatenating `ranges` ([t0, t1] in sequence time)."""
    local, cum = [], 0.0
    for t0, t1 in ranges:
        for w in all_words:
            if t0 <= w["start"] < t1:
                local.append({"word": w["word"],
                              "start": cum + (w["start"] - t0),
                              "end": cum + (w["end"] - t0)})
        cum += (t1 - t0)
    return local
