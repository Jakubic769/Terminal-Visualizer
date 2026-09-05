import pygame

from ..themes import bar_color
from .base import BaseVisualizer

ROWS = 18


class DotsGridVisualizer(BaseVisualizer):
    name = "Siatka LED"

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        bars = ctx["bars"] * ctx["sensitivity"]
        theme = ctx["theme"]
        n = len(bars)

        cell_w = rect.width / n
        cell_h = rect.height / ROWS
        radius = max(2, min(cell_w, cell_h) * 0.32)
        dim_color = tuple(int(c * 0.12) for c in theme["primary"])

        for i, v in enumerate(bars):
            v = min(1.0, v)
            lit_rows = int(v * ROWS)
            cx = rect.x + cell_w * (i + 0.5)
            for r in range(ROWS):
                cy = rect.bottom - cell_h * (r + 0.5)
                if r < lit_rows:
                    frac = r / max(1, ROWS - 1)
                    color = bar_color(theme, i, n, frac, ctx["t"])
                else:
                    color = dim_color
                pygame.draw.circle(surf, color, (int(cx), int(cy)), int(radius))
