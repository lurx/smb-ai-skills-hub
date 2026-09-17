# -*- coding: utf-8 -*-
# Cross-platform ffmpeg resolver shared by the render scripts.
# Order: $FFMPEG env -> bundled imageio-ffmpeg binary -> "ffmpeg" on PATH.
import os


def ff_bin():
    p = os.environ.get("FFMPEG")
    if p:
        return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"
