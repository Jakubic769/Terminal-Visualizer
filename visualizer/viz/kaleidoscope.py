import math

import pygame

from ..themes import bar_color
from .base import BaseVisualizer

SEGMENTS = 8


class KaleidoscopeVisualizer(BaseVisualizer):
    name = "Kalejdoskop"

    def __init__(self):
        self.rotation = 0.0

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        bars = ctx["bars"] * ctx["sensitivity"]
        theme = ctx["theme"]
        n = len(bars)
        cx, cy = rect.center
        max_r = min(rect.width, rect.height) * 0.46

        self.rotation += ctx["dt"] * (0.15 + float(sum(bars)) / max(1, n) * 0.6)

        per_seg = max(3, n // SEGMENTS)
        for seg in range(SEGMENTS):
            base_angle = self.rotation + seg * (2 * math.pi / SEGMENTS)
            mirror = seg % 2 == 0
            points_top = []
            for j in range(per_seg):
                idx = j if not mirror else per_seg - 1 - j
                v = min(1.0, bars[idx % n])
                spread = (j / max(1, per_seg - 1) - 0.5) * (math.pi / SEGMENTS)
                angle = base_angle + spread
                r = max_r * 0.15 + v * max_r * 0.85
                x = cx + math.cos(angle) * r
                y = cy + math.sin(angle) * r
                points_top.append((x, y))
                color = bar_color(theme, idx, n, v, ctx["t"])
                pygame.draw.circle(surf, color, (int(x), int(y)), 3)
            if len(points_top) > 1:
                color = theme.get("secondary") or theme.get("primary", (235, 235, 235))
                pygame.draw.aalines(surf, color, False, points_top)
