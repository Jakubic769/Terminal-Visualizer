"""Synthetic audio source: no real capture, just generates a fake 'song'
so the visualizer can be tried out with `visualizer --demo` even with no
audio playing, no pulseaudio, or on an unsupported OS."""
import time

import numpy as np


def list_apps():
    return [{"name": "Demo (syntetyczny sygnal)", "index": None}]


class DemoCapture:
    def __init__(self, sample_rate=44100, channels=2, chunk_frames=1024, app=None):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_frames = chunk_frames
        self._t = 0.0
        self._last_read = None

    def start(self):
        self._last_read = time.time()

    def read(self):
        n = self.chunk_frames
        t = self._t + np.arange(n) / self.sample_rate
        self._t += n / self.sample_rate

        bpm = 126.0
        beat_phase = (t * bpm / 60.0) % 1.0
        kick_env = np.exp(-beat_phase * 16.0)
        bass = np.sin(2 * np.pi * 55 * t) * kick_env
        pad = np.sin(2 * np.pi * 220 * t) * (0.25 + 0.2 * np.sin(2 * np.pi * 0.15 * t))
        hats = (np.random.rand(n).astype(np.float32) - 0.5) * 0.18 * (beat_phase > 0.5)
        lead = 0.22 * np.sin(2 * np.pi * (440 + 60 * np.sin(2 * np.pi * 0.2 * t)) * t)
        mono = 0.55 * bass + 0.3 * pad + hats + lead
        mono = np.tanh(mono * 1.4).astype(np.float32)

        # pace it roughly like real-time capture so consumers behave the same
        if self._last_read is not None:
            elapsed = time.time() - self._last_read
            target = n / self.sample_rate
            if elapsed < target:
                time.sleep(target - elapsed)
        self._last_read = time.time()

        stereo = np.stack([mono, mono * 0.92], axis=-1).astype(np.float32)
        return stereo

    def stop(self):
        pass
