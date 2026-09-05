import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import numpy as np
import pygame

import sys
sys.path.insert(0, os.path.dirname(__file__))

from visualizer.audio.demo import DemoCapture
from visualizer.dsp import SpectrumAnalyzer, rms
from visualizer.themes import THEMES
from visualizer.viz import VISUALIZERS

pygame.init()
pygame.display.set_mode((10, 10))  # some drivers need a display surface for font/color ops
W, H = 900, 500
BOTTOM = 74
rect = pygame.Rect(0, 0, W, H - BOTTOM)

cap = DemoCapture()
cap.start()
analyzer = SpectrumAnalyzer(chunk_size=2048, n_bars=48)

mono_buf = np.zeros(0, dtype=np.float32)
last_stereo = np.zeros((1, 2), dtype=np.float32)

# Feed a handful of chunks so the analyzer has real data (skip sleeps by
# monkeypatching time.sleep used inside DemoCapture pacing).
import time as _time
_orig_sleep = _time.sleep
_time.sleep = lambda *_a, **_k: None
for _ in range(40):
    chunk = cap.read()
    last_stereo = chunk
    mono_buf = np.concatenate([mono_buf, chunk.mean(axis=1).astype(np.float32)])
_time.sleep = _orig_sleep

bars, peaks, beat = analyzer.process(mono_buf[-2048:], dt=1/60)
waveform = mono_buf[-900:]
left_rms = rms(last_stereo[:, 0])
right_rms = rms(last_stereo[:, 1])

theme = THEMES["cava_green"]
ctx = {
    "rect": rect,
    "bars": bars,
    "peaks": peaks,
    "waveform": waveform,
    "stereo_rms": (left_rms, right_rms),
    "beat": True,
    "theme": theme,
    "t": 12.34,
    "dt": 1 / 60,
    "sensitivity": 1.0,
}

print(f"bars sample: {bars[:8]}")
print(f"beat detector fired at least once: checking each style...\n")

os.makedirs("/home/claude/visualizer/_test_out", exist_ok=True)
failures = []
for cls in VISUALIZERS:
    surf = pygame.Surface((W, H))
    surf.fill(theme["bg"])
    inst = cls()
    try:
        # draw a couple of frames so animated/stateful effects (particles, fire,
        # spectrogram, rings, kaleidoscope) accumulate something visible
        for i in range(6):
            ctx["t"] = i * 0.1
            ctx["beat"] = (i == 2)
            inst.draw(surf, ctx)
        arr = pygame.surfarray.array3d(surf)
        bg = np.array(theme["bg"])
        changed = np.any(np.abs(arr.astype(int) - bg.astype(int)) > 10, axis=-1)
        pct_changed = changed.mean() * 100
        status = "OK" if pct_changed > 0.1 else "SUSPICIOUSLY BLANK"
        print(f"{cls.name:28s} pct_pixels_drawn={pct_changed:6.2f}%  {status}")
        if pct_changed <= 0.1:
            failures.append(cls.name)
        fname = f"/home/claude/visualizer/_test_out/{cls.__name__}.png"
        pygame.image.save(surf, fname)
    except Exception as e:
        print(f"{cls.name:28s} EXCEPTION: {e!r}")
        failures.append(cls.name)

print("\n" + ("ALL GOOD" if not failures else f"FAILURES: {failures}"))
