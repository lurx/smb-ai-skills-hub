# Captions: design and rules

All captions (reels and full episode) come from ONE module, `scripts/lib_captions.py`:

```
Whisper words (local time) -> preprocess_words(fixes) -> group_words(preset) -> make_ass(preset)
```

## 1. Why fixes are applied to the word stream BEFORE grouping
Whisper's Hebrew output has recurring mishearings (brand names, English words written phonetically,
a number followed by a word that implies "percent"). If you fix them after the text is split into
2-3 word captions, a fix that spans a caption boundary never matches ("ה" at the end of one caption,
"50" at the start of the next). So:

1. `word_fixes`: whole-token replacement (`"קלוט" -> "Claude"`).
2. `prefix_aware_fixes`: substring replacement, so prefixed forms are caught too
   (`"לקלוט"`, `"שקלוט"`, `"הקלוט"` -> `"לClaude"` ...). Only applied when the token is not
   exactly the key (the exact case is handled by `word_fixes`, which may map to something else).
3. Token merging (the part that needs the continuous stream):
   - `ה` + number -> `ה-50` (one token, end time of the number)
   - `מ`/`ל` + English word (`[A-Z][A-Za-z0-9]*`) -> `מ-Claude`
   - number + a `percent_followers` word -> `50%` (the follower stays its own token)
   - number + `הם` + follower -> `50%`
4. `phrase_fixes`: multi-word replacements applied on the final caption text as a last safety net
   (useful for fixes that depend on the neighbour word).

`fixes.json` is per project. Build it by reading `whisper.json` after stage 06 and noting every
repeated error. Two or three entries usually cover 80% of the damage.

## 2. Grouping
Greedy, in reading order. Start a new caption when any of:
- group already has `max_per_group` words
- pause before this word > `max_pause` seconds (a breath = a new card)
- joined text would exceed `max_chars` (keeps the line on one row at the chosen font size)

| preset | words | pause | chars |
|---|---|---|---|
| reel (9:16) | 2 | 0.4 s | 14 |
| 1080p / 4k (16:9) | 3 | 0.6 s | 18 |

Reels use tighter groups because the viewer is on a phone and the font is huge; 2 words at a time
reads like a rhythm and keeps attention.

## 3. Timing of each card
- start = first word start - 0.05 s (lands slightly early, feels synced)
- end = next group's start - 0.02 s (no flicker gap between cards); last card = last word end + 0.6 s
- minimum card length 0.25 s

## 4. ASS style per preset
One style, bold, white fill, black outline, no shadow, bottom-centre alignment (2). Sizes are
chosen so the outline stays about 8% of the font and margins keep the text clear of platform UI.

| preset | PlayRes | font | outline | margins L/R/V |
|---|---|---|---|---|
| reel | 1080x1920 | 150 | 12 | 60 / 60 / 380 |
| 1080p | 1920x1080 | 60 | 5 | 80 / 80 / 80 |
| 4k | 3840x2160 | 120 | 10 | 160 / 160 / 160 |

`MarginV=380` on reels keeps captions above the Instagram/TikTok caption and button area.
The 4k preset is exactly 2x 1080p, so the picture is identical after scaling.

Font: `fonts.caption_font_name` (default "Secular One"). libass resolves it by installed family
name. Any bold Hebrew-capable font works; install it system-wide so ffmpeg sees it.

## 5. Hebrew and RTL
ASS/libass shapes Hebrew correctly on its own, so the caption text is written as plain logical
Hebrew (no bidi reordering). Only the lower-third PNG (drawn by PIL) needs `python-bidi`'s
`get_display()`, because PIL draws glyphs left to right.

Mixed tokens like `ה-50` or `מ-Claude` render fine: the hyphen keeps the number/English word
attached to the Hebrew prefix instead of floating to the other side of the line.

## 6. Burning
Captions are burned in a SECOND ffmpeg pass (`-vf subtitles=file.ass`) on the already-rendered
clip. ffmpeg cannot combine `subtitles=` with the `-filter_complex` that builds the clip, and the
second pass is cheap (a 30 s reel burns in seconds). Keep the `.ass` next to the mp4: if the user
reports a text error, fix `fixes.json`, regenerate, and re-burn only that reel.
