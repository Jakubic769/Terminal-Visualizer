import pygame

from ..themes import bar_color
from .base import BaseVisualizer


class MirrorBarsVisualizer(BaseVisualizer):
    name = "Slupki lustrzane"

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        bars = ctx["bars"] * ctx["sensitivity"]
        theme = ctx["theme"]
        n = len(bars)
        gap = 3
        bar_w = max(2, (rect.width - gap * (n - 1)) / n)
        mid_y = rect.centery

        for i, v in enumerate(bars):
            v = min(1.0, v)
            half_h = max(1, int(v * (rect.height / 2 - 6)))
            x = rect.x + i * (bar_w + gap)
            color = bar_color(theme, i, n, v, ctx["t"])
            pygame.draw.rect(surf, color, (x, mid_y - half_h, bar_w, half_h * 2), border_radius=2)
