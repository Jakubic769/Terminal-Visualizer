import pygame

from ..themes import bar_color
from .base import BaseVisualizer


class SpectrogramVisualizer(BaseVisualizer):
    name = "Spektrogram"

    def __init__(self):
        self._buf = None
        self._size = None
        self._accum = 0.0

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        if self._buf is None or self._size != (rect.width, rect.height):
            self._buf = pygame.Surface((rect.width, rect.height))
            self._buf.fill(ctx["theme"]["bg"])
            self._size = (rect.width, rect.height)

        bars = ctx["bars"] * ctx["sensitivity"]
        theme = ctx["theme"]
        n = len(bars)

        self._accum += ctx["dt"]
        step = max(1, int(60 * ctx["dt"] / 60 * 2))  # scroll speed, pixels/frame
        col_w = 2
        self._buf.scroll(-col_w, 0)
        pygame.draw.rect(self._buf, theme["bg"], (rect.width - col_w, 0, col_w, rect.height))

        band_h = rect.height / n
        for i, v in enumerate(bars):
            v = min(1.0, v)
            color = bar_color(theme, i, n, v, ctx["t"])
            color = tuple(int(c * (0.15 + 0.85 * v)) for c in color)
            y = rect.height - int((i + 1) * band_h)
            pygame.draw.rect(self._buf, color, (rect.width - col_w, y, col_w, int(band_h) + 1))

        surf.blit(self._buf, rect.topleft)
