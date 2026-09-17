"""Shared helpers: locate ffmpeg, load audio as a numpy array.

ffmpeg comes from imageio_ffmpeg, so nothing has to be installed with brew:
    pip3 install --user imageio-ffmpeg numpy
"""
import shutil
import subprocess
import wave

import numpy as np


def ffmpeg() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        found = shutil.which("ffmpeg")
        if found:
            return found
        raise SystemExit(
            "ffmpeg not found. pip3 install --user imageio-ffmpeg"
        )


def load_audio(path, sr=16000):
    """Decode any media file to mono float32 at `sr`."""
    tmp = "/tmp/_p2r_audio.wav"
    subprocess.run(
        [ffmpeg(), "-y", "-loglevel", "error", "-i", str(path),
         "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", tmp],
        check=True,
    )
    w = wave.open(tmp)
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return a.astype(np.float64) / 32768.0, w.getframerate()


def rms(seg) -> float:
    if len(seg) == 0:
        return 0.0
    return float(np.sqrt((seg ** 2).mean()))
