#!/usr/bin/env python3
"""Shared config loader + helpers for the podcast-episode-edit pipeline.

Every stage script imports this module. It:
  * loads config.json (path from --config, default ./config.json)
  * defines the project dir = the directory where config.json lives
  * resolves relative paths against the project dir
  * names every intermediate file in ONE place (see `paths()`)
  * offers small helpers: ffprobe, camera role lookup, source in-points

CLI usage (used by the .sh stages):
  python3 lib_config.py --config config.json get cameras.host.path
  python3 lib_config.py --config config.json path audio_track
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional

ROLES = ("host", "guest")

DEFAULTS: Dict[str, Any] = {
    "output_dir": "./work",
    "mic_cam": "host",
    "reels_cam": "guest",
    "fps": 25,
    "encoder": {
        "video_codec": "h264_videotoolbox",
        "x264_preset": "medium",
        "proxy_bitrate": "8M",
        "reel_bitrate": "10M",
        "body_bitrate": "30M",
        "body_maxrate": "40M",
        "body_bufsize": "60M",
        "intro_bitrate": "8M",
        "audio_bitrate": "192k",
    },
    "cuts": {
        "min_shot_seconds": 2.5,
        "baseline_min_shot_seconds": 1.5,
        "speak_threshold": 1.4,
        "both_threshold": 1.6,
        "correlation_margin": 0.05,
        "min_segment_seconds": 0.4,
    },
    "sync": {"window_seconds": 300},
    "trim": {"voice_db_above_floor": 12, "pad_before": 0.5, "pad_after": 1.0},
    "split_screen": {
        "enabled": True,
        "intro_seconds": 30.0,
        "outro_seconds": 30.0,
        "hook_seconds": 5.0,
    },
    "color_grade": {
        "enabled": True,
        "curves": "curves=master='0/0.03 0.5/0.50 1/0.96':"
                  "red='0/0.02 0.4/0.43 0.7/0.73 1/1':"
                  "green='0/0 0.5/0.50 1/0.98':"
                  "blue='0/0.04 0.4/0.42 0.7/0.65 1/0.94'",
        "eq": "eq=contrast=1.06:saturation=1.10:gamma=0.98",
    },
    "whisper": {
        "model": "whisper-1",
        "language": "he",
        "chunk_seconds": 600,
    },
    "fonts": {"caption_font_name": "Secular One"},
    "captions": {"fixes_file": "./fixes.json"},
    "hooks_file": "./hooks.json",
    "lower_third": {
        "name": "",
        "title": "",
        "show_seconds": 8,
        "font_path": "",
        "bar_color": [0, 0, 0, 200],
        "accent_color": [255, 200, 50, 255],
        "name_color": [255, 255, 255, 255],
        "title_color": [220, 220, 220, 255],
    },
    "intro_audio": "",
    "outro_audio": "",
}


def _deep_merge(base: Dict[str, Any], over: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


class Config:
    def __init__(self, config_path: str):
        config_path = os.path.abspath(os.path.expanduser(config_path))
        if not os.path.isfile(config_path):
            die(f"config not found: {config_path}\n"
                f"   copy config.example.json -> config.json and fill in your camera paths")
        with open(config_path, encoding="utf-8") as f:
            try:
                raw = json.load(f)
            except json.JSONDecodeError as e:
                die(f"config.json is not valid JSON: {e}")
        self.path = config_path
        self.project_dir = os.path.dirname(config_path)
        self.data = _deep_merge(DEFAULTS, raw)
        self._validate()

    # ---- access -------------------------------------------------------
    def get(self, dotted: str, default: Any = None) -> Any:
        cur: Any = self.data
        for part in dotted.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

    def resolve(self, p: str) -> str:
        """Resolve a path from config: ~ expanded, relative = project dir."""
        p = os.path.expanduser(p)
        if not os.path.isabs(p):
            p = os.path.join(self.project_dir, p)
        return os.path.normpath(p)

    @property
    def output_dir(self) -> str:
        d = self.resolve(self.get("output_dir"))
        os.makedirs(d, exist_ok=True)
        return d

    def out(self, name: str) -> str:
        return os.path.join(self.output_dir, name)

    # ---- cameras ------------------------------------------------------
    def cam(self, role: str) -> Dict[str, Any]:
        cams = self.get("cameras") or {}
        if role not in cams:
            die(f"config.cameras has no '{role}' entry")
        return cams[role]

    def cam_path(self, role: str) -> str:
        p = self.resolve(self.cam(role)["path"])
        if not os.path.isfile(p):
            die(f"camera file for '{role}' not found: {p}")
        return p

    @property
    def mic_cam(self) -> str:
        return self.get("mic_cam")

    @property
    def other_cam(self) -> str:
        return "guest" if self.mic_cam == "host" else "host"

    @property
    def reels_cam(self) -> str:
        return self.get("reels_cam")

    # ---- file names (single source of truth) --------------------------
    def paths(self) -> Dict[str, str]:
        o = self.out
        p = {
            "sync_offset": o("sync_offset.txt"),
            "trim": o("trim.txt"),
            "cuts": o("cuts.json"),
            "cuts_final": o("cuts_final.json"),
            "audio_track": o("audio_track.m4a"),
            "chunks_dir": o("chunks"),
            "whisper": o("whisper.json"),
            "guest_blocks": o("guest_blocks.json"),
            "guest_text": o("guest_text.txt"),
            "body": o("body.mp4"),
            "body_filter": o("body_filter.txt"),
            "intro": o("intro.mp4"),
            "outro": o("outro.mp4"),
            "final": o("final.mp4"),
            "reels_dir": o("reels"),
            "lower_third_png": o("lower_third.png"),
            "full_subs": o("full_subs.ass"),
            "hooks": self.resolve(self.get("hooks_file")),
            "fixes": self.resolve(self.get("captions.fixes_file")),
        }
        for role in ROLES:
            p[f"pcm_{role}"] = o(f"{role}_8k.pcm")
            p[f"motion_{role}"] = o(f"motion_{role}.npy")
            p[f"proxy_{role}"] = o(f"proxy_{role}.mp4")
        return p

    # ---- encoder ------------------------------------------------------
    def video_codec_args(self, bitrate: str, maxrate: Optional[str] = None,
                         bufsize: Optional[str] = None) -> List[str]:
        codec = self.get("encoder.video_codec")
        args = ["-c:v", codec, "-b:v", bitrate]
        if maxrate:
            args += ["-maxrate", maxrate]
        if bufsize:
            args += ["-bufsize", bufsize]
        if codec == "libx264":
            args += ["-preset", self.get("encoder.x264_preset")]
        args += ["-tag:v", "avc1", "-pix_fmt", "yuv420p"]
        return args

    # ---- validation ---------------------------------------------------
    def _validate(self) -> None:
        cams = self.get("cameras")
        if not isinstance(cams, dict) or not all(r in cams for r in ROLES):
            die("config.cameras must contain both 'host' and 'guest'")
        if self.mic_cam not in ROLES:
            die("config.mic_cam must be 'host' or 'guest'")
        if self.reels_cam not in ROLES:
            die("config.reels_cam must be 'host' or 'guest'")


# ---- generic helpers ----------------------------------------------------
def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def require_file(path: str, produced_by: str) -> str:
    if not os.path.isfile(path):
        die(f"missing input: {path}\n   run {produced_by} first")
    return path


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        die(f"'{name}' not found in PATH. install it first (brew install ffmpeg / apt install ffmpeg)")


def ffprobe_video(path: str) -> Dict[str, Any]:
    """Return {'width','height','duration','fps'} for the first video stream."""
    require_tool("ffprobe")
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=width,height,r_frame_rate:format=duration",
           "-of", "json", path]
    d = json.loads(subprocess.check_output(cmd, text=True))
    st = d["streams"][0]
    num, den = st["r_frame_rate"].split("/")
    return {
        "width": int(st["width"]),
        "height": int(st["height"]),
        "duration": float(d["format"]["duration"]),
        "fps": float(num) / float(den or 1),
    }


def ffprobe_duration(path: str) -> float:
    require_tool("ffprobe")
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", path]
    return float(subprocess.check_output(cmd, text=True).strip())


def load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def source_in_points(cfg: Config, cuts_doc: Dict[str, Any]) -> Dict[str, float]:
    """Map role -> source-file timestamp of sequence time 0.

    cuts.json stores trim_in/trim_out on the MIC camera's timeline and
    sync_offset = mic_time - other_time. So:
        mic   source in-point = trim_in
        other source in-point = trim_in - sync_offset
    """
    trim_in = float(cuts_doc["trim_in"])
    sync = float(cuts_doc["sync_offset"])
    return {cfg.mic_cam: trim_in, cfg.other_cam: trim_in - sync}


def base_parser(description: str) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=description,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="./config.json",
                    help="path to config.json (default ./config.json; its folder is the project dir)")
    return ap


# ---- CLI for shell scripts ---------------------------------------------
def _main() -> None:
    ap = base_parser("config helper for shell stages")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get", help="print a config value by dotted key")
    g.add_argument("key")
    g.add_argument("--resolve", action="store_true", help="treat value as a path and resolve it")
    p = sub.add_parser("path", help="print an intermediate file path by name (see paths())")
    p.add_argument("name")
    sub.add_parser("output_dir", help="print the resolved output dir")
    sub.add_parser("project_dir", help="print the project dir")
    c = sub.add_parser("campath", help="print the resolved camera path for a role")
    c.add_argument("role", choices=ROLES)
    sub.add_parser("codec_args", help="print proxy-quality encoder args, one per line")
    a = ap.parse_args()
    cfg = Config(a.config)
    if a.cmd == "get":
        v = cfg.get(a.key)
        if v is None:
            sys.exit(1)
        if a.resolve:
            v = cfg.resolve(str(v))
        print(json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
    elif a.cmd == "path":
        print(cfg.paths()[a.name])
    elif a.cmd == "output_dir":
        print(cfg.output_dir)
    elif a.cmd == "project_dir":
        print(cfg.project_dir)
    elif a.cmd == "campath":
        print(cfg.cam_path(a.role))
    elif a.cmd == "codec_args":
        print("\n".join(cfg.video_codec_args(cfg.get("encoder.proxy_bitrate"))))


if __name__ == "__main__":
    _main()
