import numpy as np
import pygame

from .base import BaseVisualizer

GRID_W = 90
GRID_H = 46


class FireVisualizer(BaseVisualizer):
    name = "Ogien"

    def __init__(self):
        self.heat = np.zeros((GRID_H, GRID_W), dtype=np.float32)
        self._small_surf = pygame.Surface((GRID_W, GRID_H))

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        bars = ctx["bars"] * ctx["sensitivity"]
        theme = ctx["theme"]
        n = len(bars)

        # inject heat at the bottom row, one column group per bar
        cols_per_bar = max(1, GRID_W // n)
        for i, v in enumerate(bars):
            v = min(1.0, v)
            x0 = i * cols_per_bar
            x1 = min(GRID_W, x0 + cols_per_bar)
            self.heat[GRID_H - 1, x0:x1] = np.clip(v * 1.3 + np.random.rand(max(1, x1 - x0)) * 0.15, 0, 1)

        # propagate upward with cooling + slight horizontal drift (doom-fire style)
        cooling = 0.045
        new_heat = self.heat.copy()
        shift = np.random.randint(-1, 2, size=(GRID_H - 1, GRID_W))
        for y in range(GRID_H - 1):
            src_row = self.heat[y + 1]
            shifted = np.take(src_row, (np.arange(GRID_W) + shift[y]) % GRID_W)
            new_heat[y] = np.clip(shifted - cooling * np.random.rand(GRID_W), 0, 1)
        self.heat = new_heat

        palette = _fire_palette(theme)
        idx = np.clip((self.heat * (len(palette) - 1)).astype(np.int32), 0, len(palette) - 1)
        pix = palette[idx]  # (H, W, 3)

        pygame.surfarray.blit_array(self._small_surf, np.transpose(pix, (1, 0, 2)))
        scaled = pygame.transform.smoothscale(self._small_surf, (rect.width, rect.height))
        surf.blit(scaled, rect.topleft)


_palette_cache = {}


def _fire_palette(theme):
    key = theme.get("label")
    if key in _palette_cache:
        return _palette_cache[key]
    bg = np.array(theme["bg"], dtype=np.float32)
    primary = np.array(theme["primary"], dtype=np.float32)
    secondary = np.array(theme.get("secondary", (255, 255, 200)), dtype=np.float32)
    white = np.array([255, 255, 245], dtype=np.float32)
    steps = 128
    stops = [bg, bg, primary * 0.5, primary, secondary, white]
    seg = steps // (len(stops) - 1)
    colors = []
    for i in range(len(stops) - 1):
        for t in range(seg):
            f = t / seg
            colors.append(stops[i] * (1 - f) + stops[i + 1] * f)
    while len(colors) < steps:
        colors.append(white)
    palette = np.clip(np.array(colors[:steps]), 0, 255).astype(np.uint8)
    _palette_cache[key] = palette
    return palette
