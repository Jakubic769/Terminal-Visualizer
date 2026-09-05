import pygame

from ..themes import bar_color
from .base import BaseVisualizer


class RingsVisualizer(BaseVisualizer):
    name = "Pulsujace pierscienie"

    def __init__(self):
        self.ripples = []  # list of [radius, alpha]

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        bars = ctx["bars"] * ctx["sensitivity"]
        theme = ctx["theme"]
        cx, cy = rect.center
        max_r = min(rect.width, rect.height) * 0.48

        if ctx["beat"]:
            self.ripples.append([min(rect.width, rect.height) * 0.08, 255])

        for ripple in self.ripples:
            ripple[0] += 260 * ctx["dt"]
            ripple[1] -= 260 * ctx["dt"]
        self.ripples = [r for r in self.ripples if r[1] > 0 and r[0] < max_r]

        for radius, alpha in self.ripples:
            color = bar_color(theme, int(radius) % len(bars), len(bars), 1.0, ctx["t"])
            ring_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*color, int(max(0, alpha))), (rect.width // 2, rect.height // 2),
                                int(radius), 3)
            surf.blit(ring_surf, rect.topleft)

        n = len(bars)
        for i in range(0, n, max(1, n // 24)):
            v = min(1.0, bars[i])
            r = max_r * 0.35 + v * max_r * 0.5
            color = bar_color(theme, i, n, v, ctx["t"])
            pygame.draw.circle(surf, color, (cx, cy), int(r), 2)
