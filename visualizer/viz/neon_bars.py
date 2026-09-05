import pygame

from ..themes import bar_color
from .base import BaseVisualizer


class NeonBarsVisualizer(BaseVisualizer):
    name = "Neonowe slupki"

    def __init__(self):
        self._glow = None
        self._glow_size = None

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        if self._glow is None or self._glow_size != (rect.width, rect.height):
            self._glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            self._glow_size = (rect.width, rect.height)
        glow = self._glow
        glow.fill((0, 0, 0, 0))

        bars = ctx["bars"] * ctx["sensitivity"]
        theme = ctx["theme"]
        n = len(bars)
        gap = 4
        bar_w = max(2, (rect.width - gap * (n - 1)) / n)

        for i, v in enumerate(bars):
            v = min(1.0, v)
            h = max(2, int(v * (rect.height - 10)))
            x = int(i * (bar_w + gap))
            y = rect.height - h
            color = bar_color(theme, i, n, v, ctx["t"])

            # outer soft glow (wide, low alpha)
            pygame.draw.rect(glow, (*color, 55), (x - 4, y - 4, bar_w + 8, h + 8), border_radius=8)
            # mid glow
            pygame.draw.rect(glow, (*color, 110), (x - 1, y - 1, bar_w + 2, h + 2), border_radius=5)
            # bright core
            pygame.draw.rect(glow, (*color, 255), (x, y, bar_w, h), border_radius=3)

        surf.blit(glow, rect.topleft)
