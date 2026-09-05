import pygame

from ..themes import bar_color
from .base import BaseVisualizer


class BarsVisualizer(BaseVisualizer):
    name = "Slupki (Cava)"

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        bars = ctx["bars"] * ctx["sensitivity"]
        peaks = ctx["peaks"]
        theme = ctx["theme"]
        n = len(bars)
        gap = 3
        bar_w = max(2, (rect.width - gap * (n - 1)) / n)

        for i, v in enumerate(bars):
            v = min(1.0, v)
            h = max(2, int(v * (rect.height - 10)))
            x = rect.x + i * (bar_w + gap)
            y = rect.bottom - h
            color = bar_color(theme, i, n, v, ctx["t"])
            pygame.draw.rect(surf, color, (x, y, bar_w, h), border_radius=2)

            # peak-hold cap
            peak_y = rect.bottom - int(peaks[i] * (rect.height - 10))
            pygame.draw.rect(surf, theme.get("text", (255, 255, 255)),
                              (x, peak_y - 2, bar_w, 2))
