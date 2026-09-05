import random

import pygame

from ..themes import bar_color
from .base import BaseVisualizer


class ParticlesVisualizer(BaseVisualizer):
    name = "Czasteczki"

    def __init__(self):
        self.particles = []  # dict: x, y, vx, vy, life, max_life, size, color_seed

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        bars = ctx["bars"] * ctx["sensitivity"]
        theme = ctx["theme"]
        dt = ctx["dt"]
        n = len(bars)

        energy = float(sum(bars) / max(1, n))
        spawn_count = int(energy * 14) + (18 if ctx["beat"] else 0)
        for _ in range(spawn_count):
            i = random.randrange(n)
            v = min(1.0, bars[i])
            if v < 0.08:
                continue
            x = rect.x + (i / n) * rect.width + random.uniform(-6, 6)
            self.particles.append({
                "x": x,
                "y": rect.bottom - random.uniform(0, 10),
                "vx": random.uniform(-20, 20),
                "vy": -random.uniform(60, 220) * (0.5 + v),
                "life": 0.0,
                "max_life": random.uniform(0.8, 1.8),
                "size": random.uniform(2, 5) + v * 4,
                "idx": i,
            })

        alive = []
        for p in self.particles:
            p["life"] += dt
            if p["life"] >= p["max_life"]:
                continue
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 40 * dt  # gentle gravity
            alive.append(p)
        self.particles = alive[-600:]

        for p in self.particles:
            frac = 1.0 - p["life"] / p["max_life"]
            color = bar_color(theme, p["idx"], n, frac, ctx["t"])
            r = max(1, int(p["size"] * frac))
            pygame.draw.circle(surf, color, (int(p["x"]), int(p["y"])), r)
