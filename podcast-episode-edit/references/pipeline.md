# Pipeline: data flow and debugging

## Timelines (read this first)

Three clocks exist. Mixing them is the #1 source of bugs.

| clock | meaning | who uses it |
|---|---|---|
| mic cam source time | seconds from the start of the mic camera file | `trim.txt`, `sync_offset.txt` |
| other cam source time | seconds from the start of the other camera file | derived only: `other_t = mic_t - sync_offset` |
| **sequence time** | seconds from the episode IN point (`trim_in`), the final timeline of `body.mp4` | `cuts*.json`, `whisper.json`, `hooks.json`, `audio_track.m4a`, captions |

`cuts.json` stores the anchor once: `{"trim_in","trim_out","sync_offset","duration"}`. Every later
stage converts `sequence -> source` with `lib_config.source_in_points()`:

```
src_in[mic]   = trim_in
src_in[other] = trim_in - sync_offset
source_time   = src_in[cam] + sequence_time
```

`sync_offset = mic_time - other_time` (positive = the mic camera started recording later).

## Data flow

```
host_cam.mp4 ─┬─► 00 extract ─► host_8k.pcm ──┐
guest_cam.mp4 ┴─► 00 extract ─► guest_8k.pcm ─┤
                                              ├─► 01 sync ─► sync_offset.txt ─┐
                   mic pcm ───────────────────┴─► 02 trim ─► trim.txt ────────┤
cams + face_roi ─► 03 motion ─► motion_host.npy, motion_guest.npy ───────────┤
                                                                              ▼
                                                               04 cuts_base ─► cuts.json (header + baseline segments)
cams + trim + sync ─► 05 proxies ─► proxy_host.mp4, proxy_guest.mp4, audio_track.m4a
audio_track ─► 06 transcribe ─► chunks/chunk_NN.{mp3,json} ─► whisper.json
cuts + whisper ─► 07 find_hooks ─► guest_blocks.json, guest_text.txt  ──(human)──► hooks.json
cuts + whisper + audio_track + motion ─► 08 cuts_audio_correlation ─► cuts_final.json
cams + cuts_final + hooks + audio_track ─► 09 render_body ─► body_filter.txt, body.mp4
intro.mp3/outro.mp3 + body (for size) ─► 10 intro_outro ─► intro.mp4, outro.mp4
intro + body + outro ─► 11 concat ─► final.mp4
reels cam + audio_track + hooks + whisper + fixes ─► 12 render_reels ─► reels/reel_<slug>.{mp4,ass}
config.lower_third ─► 13 lower_thirds ─► lower_third.png  (--apply ─► final_lt.mp4)
cuts + whisper + fixes ─► 14 full_subs ─► full_subs.ass   (--burn ─► final_subs.mp4)
```

## Stage by stage

### 00 extract audio
ffmpeg, each camera -> 8 kHz mono s16le PCM. Small (about 1 MB per minute) and fast to load with numpy.

### 01 sync (cross-correlation)
Normalise both signals, take a 300 s window from the middle of each (silent heads/tails would
mislead), FFT cross-correlate, take the peak lag, convert the window lag back to a global offset.
Debug: if the printed offset is wildly off (minutes), one camera probably has no usable audio;
raise `sync.window_seconds` or check that both cameras recorded the room.

### 02 trim (voice activity)
RMS per 100 ms frame in dB. Noise floor = 5th percentile. Voiced = floor + 12 dB. Smooth with a
5 s window, "substantial" = more than 60% voiced. First/last substantial frame = IN/OUT, padded
0.5 s / 1.0 s. Debug: open `trim.txt`, it is two numbers; edit by hand if the detection caught a
soundcheck. Later stages just read the file.

### 03 motion
Per camera: crop `face_roi`, scale to 64x64 gray at 4 fps, frame-to-frame absolute difference summed
over pixels. Index i = time i/4 s in that camera's source time. Debug: `np.load(...)` and plot, or
check p95 vs max in the printout; a flat signal means the ROI misses the face. Grab a still with
`ffmpeg -ss 600 -i cam.mp4 -frames:v 1 still.jpg` and measure the face box as fractions of the frame.

### 04 cuts_base
Resample both motion signals onto the mic-cam timeline for the trim range, 1 s rolling mean,
divide by each camera's own median (so a wide shot and a close shot are comparable). Per 0.25 s:
BOTH if both > 1.6, else the active one (> 1.4) with hysteresis (the other must be 20% higher to
switch), else stay. Runs shorter than 1.5 s merge into the longer neighbour. Output includes the
timing header every later stage depends on. Debug: the printed camera split; one camera at 90%+
means thresholds or ROI are off.

### 05 proxies
1080p proxies of both cameras for the trim range (fast-seek `-ss` before `-i`) and
`audio_track.m4a` (mic cam, AAC 48 kHz stereo). The proxies are for previewing; the final render
reads the originals.

### 06 transcribe
Split `audio_track.m4a` into `chunk_seconds` mp3 chunks (mono 16 kHz 64 kbps, stays far below the
25 MB API limit), send each to `whisper-1` with `verbose_json` and word + segment timestamps,
cache each response as `chunk_NN.json`, merge with offset `N * chunk_seconds`. Rerunning only
transcribes missing chunks. `--from-json` skips entirely when `whisper.json` exists.
Debug: a chunk whose words all have the same timestamp means the API returned without word
granularity; delete its json and rerun.

### 07 find_hooks
Walks the reels-cam segments of `cuts.json`, collects the Whisper words inside each, writes a
readable `guest_text.txt` with `[mm:ss-mm:ss]` brackets. The human (or Claude in conversation)
picks hooks from it and writes `hooks.json`.

### 08 cuts_audio_correlation
For each Whisper segment (>= 0.4 s): audio RMS per 250 ms vs each camera's motion (also 250 ms),
Pearson correlation, pick the camera whose motion follows the sound (margin 0.05, otherwise keep
the previous camera). Gaps between segments inherit the previous camera, neighbours collapse,
min shot 2.5 s. This is usually much better than stage 04 because listening-reactions produce
motion that does not track the audio envelope.

### 09 render_body
Builds `blocks`: split-screen windows (first N s, hook_seconds after each hook start, last N s)
and single-camera segments in between, clipped from `cuts_final.json`. Each block becomes a
`trim,setpts,setsar,fps` chain on the ORIGINAL camera input (index 0 = host, 1 = guest); split
blocks crop each camera to half width (`split_crop_x`) and `hstack`. All chains `concat`, then the
colour grade (`curves` + `eq`). Audio is mapped straight from `audio_track.m4a`.
Debug: `--dry-run` writes only `body_filter.txt`; inspect it. Overlapping split windows abort with
a clear message (move a hook). "BOTH" segments from the baseline render as host.

### 10 intro_outro
`lavfi color=black` at the body's exact WxH and fps for the mp3's ffprobe duration, mp3 muxed in.
No mp3 configured -> skipped and any stale intro/outro is deleted so 11 does not pick it up.

### 11 concat
concat FILTER (not the demuxer) so differently-encoded parts are safe. Re-encodes the whole
episode once at body bitrate.

### 12 render_reels
Per hook: three stills per range through a Haar frontal-face cascade, median face X, crop
`height*9/16 x height` around it (clamped to the frame), fallback = centre. Pass 1 renders
video+audio (multi-range hooks concat inside one filter_complex). Pass 2 burns the ASS made by
`lib_captions` with the `reel` preset. `--no-subs` stops after pass 1. `--only slug` for a pilot.

### 13 lower_thirds
PIL draws a rounded translucent bar + accent stripe + right-aligned bidi-shaped name/title.
`--res 1080p|4k`. `--apply` overlays it on `final.mp4` for `show_seconds`.

### 14 full_subs
Same caption module, preset `1080p` or `4k`, optional offset = intro length so the ASS lines up
with `final.mp4`. `--burn` creates `final_subs.mp4`.

## Debugging any stage
1. Run the stage alone with `--config`; every missing input names the stage that produces it.
2. Outputs are plain files: `.txt` (two numbers), `.json`, `.npy`, `.ass`. Open them.
3. ffmpeg errors: rerun the printed stage with `-loglevel info` by editing the script locally,
   or copy the command. For stage 09, `--dry-run` then
   `ffmpeg -i host -i guest -i audio -filter_complex_script work/body_filter.txt -t 60 -f null -`
   validates the graph in about a minute without a full render.
4. Encoder not found (`h264_videotoolbox`): not on a Mac; set `encoder.video_codec` to `libx264`.
5. Subtitles not rendering: libass could not find `fonts.caption_font_name`; run `fc-list | grep -i secular`.
