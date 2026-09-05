import math

import pygame

from ..themes import bar_color
from .base import BaseVisualizer


class CircularVisualizer(BaseVisualizer):
    name = "Spektrum kolowe"

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        bars = ctx["bars"] * ctx["sensitivity"]
        theme = ctx["theme"]
        n = len(bars)
        cx, cy = rect.center
        base_r = min(rect.width, rect.height) * 0.18
        max_len = min(rect.width, rect.height) * 0.32

        pygame.draw.circle(surf, theme.get("secondary") or theme.get("primary", (235, 235, 235)), (cx, cy), int(base_r), 2)

        for i, v in enumerate(bars):
            v = min(1.0, v)
            angle = (i / n) * 2 * math.pi - math.pi / 2
            length = base_r + v * max_len
            x1 = float(cx + math.cos(angle) * base_r)
            y1 = float(cy + math.sin(angle) * base_r)
            x2 = float(cx + math.cos(angle) * length)
            y2 = float(cy + math.sin(angle) * length)
            color = bar_color(theme, i, n, v, ctx["t"])
            pygame.draw.line(surf, color, (x1, y1), (x2, y2), 4)
