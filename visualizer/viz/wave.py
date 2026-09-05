import numpy as np
import pygame

from .base import BaseVisualizer


class WaveVisualizer(BaseVisualizer):
    name = "Oscyloskop"

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        wf = ctx["waveform"]
        theme = ctx["theme"]
        sens = ctx["sensitivity"]
        if wf is None or len(wf) < 2:
            return

        color = theme["primary"] if not theme.get("dynamic") else _rainbow(ctx["t"])
        n = len(wf)
        step = rect.width / (n - 1)
        mid = rect.centery
        amp = (rect.height / 2 - 8) * sens

        points = [
            (rect.x + i * step, mid - float(np.clip(s, -1.2, 1.2)) * amp)
            for i, s in enumerate(wf)
        ]
        if len(points) >= 2:
            pygame.draw.aalines(surf, theme.get("secondary", color), False, points)
            pygame.draw.lines(surf, color, False, points, 3)


def _rainbow(t):
    from ..themes import hue
    return hue(t * 0.1)
