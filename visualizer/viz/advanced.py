"""Generated family of additional audio-reactive visual styles.

The styles share one renderer but each preset uses different geometry and motion.
This keeps the project lightweight while providing many distinct visual modes.
"""
import math
import random

import pygame

from ..themes import bar_color
from .base import BaseVisualizer


_PRESETS = [
    ("Fala neonowa", "wave"), ("Fala lustrzana", "wave_mirror"), ("Fala podwojna", "wave_double"),
    ("Gora dol", "mountain"), ("Gora spektrum", "mountain_ring"), ("Radar", "radar"),
    ("Radar puls", "radar_pulse"), ("Orbity", "orbits"), ("Orbity beat", "orbits_beat"),
    ("Galaktyka", "galaxy"), ("Gwiezdny wir", "starfield"), ("Tunnel", "tunnel"),
    ("Tunnel beat", "tunnel_beat"), ("Spirala", "spiral"), ("Podwojna spirala", "spiral2"),
    ("Kwiat", "flower"), ("Kwiat puls", "flower_pulse"), ("Rozeta", "rosette"),
    ("Sloneczko", "sunburst"), ("Korona", "crown"), ("Korona beat", "crown_beat"),
    ("Hexagon", "hex"), ("Hexagon puls", "hex_pulse"), ("Kryształy", "crystals"),
    ("Diamenty", "diamonds"), ("Diamenty wir", "diamonds_spin"), ("Licznik", "meter"),
    ("Fale pionowe", "vertical_wave"), ("Fale poziome", "horizontal_wave"), ("Schody", "stairs"),
    ("Schody lustrzane", "stairs_mirror"), ("Macierz", "matrix"), ("Matrix deszcz", "matrix_rain"),
    ("Equalizer szeroki", "wide_bars"), ("Equalizer waski", "thin_bars"), ("Equalizer neon", "neon_levels"),
    ("Pillars", "pillars"), ("Pulsujace kolumny", "pulsing_columns"), ("Kolo zebate", "gear"),
    ("Kolo zebate puls", "gear_pulse"), ("Wir", "vortex"), ("Wir RGB", "vortex_rgb"),
    ("Mikser", "mixer"), ("Mikser lustro", "mixer_mirror"), ("Skaner", "scanner"),
    ("Skaner dual", "scanner_dual"), ("Perkusja", "drum"), ("Perkusja okragla", "drum_ring"),
    ("Impuls", "impulse"), ("Impuls 3D", "impulse_3d"),
]


def _mix(a, b, f):
    return tuple(int(a[i] * (1 - f) + b[i] * f) for i in range(3))


class AdvancedVisualizer(BaseVisualizer):
    preset_name = "Dodatkowy"
    mode = "wave"

    def __init__(self):
        self.phase = random.random() * math.tau
        self.rotation = random.random() * math.tau
        self.points = []

    def draw(self, surf, ctx):
        mode = self.mode
        if mode.startswith("wave"):
            self._wave(surf, ctx, mode)
        elif mode.startswith("mountain"):
            self._mountain(surf, ctx, mode)
        elif mode.startswith("radar"):
            self._radar(surf, ctx, mode)
        elif mode.startswith("orbits") or mode == "galaxy" or mode == "starfield":
            self._orbits(surf, ctx, mode)
        elif mode.startswith("tunnel"):
            self._tunnel(surf, ctx, mode)
        elif mode.startswith("spiral"):
            self._spiral(surf, ctx, mode)
        elif mode.startswith("flower") or mode in {"rosette", "sunburst", "crown", "crown_beat"}:
            self._flower(surf, ctx, mode)
        elif mode.startswith("hex"):
            self._hex(surf, ctx, mode)
        elif mode in {"crystals", "diamonds", "diamonds_spin"}:
            self._diamonds(surf, ctx, mode)
        elif mode == "meter":
            self._meter(surf, ctx)
        elif mode in {"vertical_wave", "horizontal_wave", "stairs", "stairs_mirror"}:
            self._gridwave(surf, ctx, mode)
        elif mode in {"matrix", "matrix_rain"}:
            self._matrix(surf, ctx, mode)
        elif mode.startswith("equalizer") or mode in {"pillars", "pulsing_columns"}:
            self._bars(surf, ctx, mode)
        elif mode.startswith("gear"):
            self._gear(surf, ctx, mode)
        elif mode.startswith("vortex"):
            self._vortex(surf, ctx, mode)
        elif mode.startswith("mixer"):
            self._mixer(surf, ctx, mode)
        elif mode.startswith("scanner"):
            self._scanner(surf, ctx, mode)
        elif mode.startswith("drum"):
            self._drum(surf, ctx, mode)
        elif mode.startswith("impulse"):
            self._impulse(surf, ctx, mode)
        else:
            self._orb(surf, ctx)

    def _base(self, ctx):
        rect, bars = ctx["rect"], ctx["bars"] * ctx["sensitivity"]
        bars = [min(1.0, float(v)) for v in bars]
        theme, t = ctx["theme"], ctx["t"]
        return rect, bars, theme, t

    def _wave(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        wf = ctx["waveform"]
        n = len(wf)
        pts = []
        amp = rect.height * 0.36 * ctx["sensitivity"]
        for i, value in enumerate(wf[::4]):
            x = rect.x + i * rect.width / max(1, len(wf[::4]) - 1)
            y = rect.centery - float(value) * amp
            if mode == "wave_mirror":
                y = rect.centery - abs(float(value)) * amp
            elif mode == "wave_double":
                y = rect.centery - math.sin(t * 2.0 + i * 0.08) * abs(float(value)) * amp
            pts.append((x, y))
        color = bar_color(theme, 0, max(1, len(bars)), 0.75, t)
        if len(pts) > 1:
            pygame.draw.aalines(surf, color, False, pts)
            if mode == "wave_double":
                pygame.draw.aalines(surf, theme["secondary"], False, [(x, 2 * rect.centery - y) for x, y in pts])

    def _mountain(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        n = len(bars)
        points = [(rect.x, rect.bottom)]
        for i, v in enumerate(bars):
            x = rect.x + (i / max(1, n - 1)) * rect.width
            y = rect.bottom - v * rect.height * 0.86
            if mode == "mountain_ring":
                y -= math.sin(t * 1.4 + i * 0.2) * v * 8
            points.append((x, y))
        points.append((rect.right, rect.bottom))
        pygame.draw.polygon(surf, (*theme["primary"], 70), points)
        pygame.draw.lines(surf, theme["primary"], False, points[1:-1], 3)

    def _radar(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        r = min(rect.width, rect.height) * 0.42
        for k in range(4):
            pygame.draw.circle(surf, _mix(theme["primary"], theme["bg"], 0.45), (cx, cy), int(r * (k + 1) / 4), 1)
        angle = self.rotation + t * (0.8 if mode == "radar" else 1.8)
        ex = cx + math.cos(angle) * r
        ey = cy + math.sin(angle) * r
        pygame.draw.line(surf, theme["primary"], (cx, cy), (ex, ey), 2)
        n = len(bars)
        for i, v in enumerate(bars[::2]):
            a = 2 * math.pi * (i * 2) / n
            rr = r * (0.3 + v * 0.7)
            x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
            pygame.draw.circle(surf, bar_color(theme, i, max(1, n), v, t), (int(x), int(y)), 2)

    def _orbits(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        max_r = min(rect.width, rect.height) * 0.43
        count = 7 if mode != "starfield" else 11
        for j in range(count):
            phase = self.phase + t * (0.25 + j * 0.035)
            radius = max_r * (0.12 + (j + 1) / count * 0.82)
            if mode == "galaxy":
                radius *= 0.75 + 0.25 * math.sin(t + j)
            pygame.draw.ellipse(surf, _mix(theme["secondary"], theme["primary"], j / count),
                                (cx - radius, cy - radius * 0.45, radius * 2, radius * 0.9), 1)
            for i in range(3):
                idx = (j * 3 + i) % max(1, len(bars))
                rr = radius
                ang = phase + i * math.tau / 3
                x = cx + math.cos(ang) * rr
                y = cy + math.sin(ang) * rr * 0.45
                v = bars[idx]
                c = bar_color(theme, idx, max(1, len(bars)), v, t)
                size = 2 + int(4 * v)
                pygame.draw.circle(surf, c, (int(x), int(y)), size)

    def _tunnel(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        layers = 13
        for k in range(layers):
            p = ((t * (0.16 if mode == "tunnel" else 0.34)) + k / layers) % 1.0
            r = (0.06 + p * 0.68) * min(rect.width, rect.height)
            col = bar_color(theme, k, layers, 1.0 - p, t)
            pygame.draw.rect(surf, col, (cx - r, cy - r * 0.55, 2 * r, 1.1 * r), 2)

    def _spiral(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        n = max(40, len(bars) * 2)
        prev = None
        for i in range(n):
            v = bars[i % len(bars)]
            a = i * 0.42 + t * (0.9 if mode == "spiral" else -0.65)
            r = 4 + i / n * min(rect.width, rect.height) * 0.45 + v * 32
            p = (cx + math.cos(a) * r, cy + math.sin(a) * r)
            if prev:
                pygame.draw.line(surf, bar_color(theme, i, n, v, t), prev, p, 2)
            prev = p

    def _flower(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        n = len(bars)
        petals = 32
        pts = []
        for i in range(petals + 1):
            a = i / petals * math.tau + t * 0.15
            idx = int(i * n / petals) % n
            v = bars[idx]
            r = min(rect.width, rect.height) * (0.12 + 0.34 * v)
            if mode == "flower_pulse":
                r *= 0.85 + 0.15 * math.sin(t * 3.0)
            if mode == "sunburst":
                r += min(rect.width, rect.height) * 0.13
            if mode.startswith("crown"):
                r = min(rect.width, rect.height) * (0.18 + 0.36 * v)
                a = -math.pi / 2 + (i / petals - 0.5) * math.pi
            x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
            pts.append((x, y))
        if mode == "rosette":
            pygame.draw.polygon(surf, _mix(theme["primary"], theme["secondary"], 0.4), pts)
        else:
            pygame.draw.aalines(surf, theme["primary"], False, pts)
        pygame.draw.circle(surf, theme["secondary"], (cx, cy), 8 + int(sum(bars) / n * 12))

    def _hex(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        n = len(bars)
        rings = 6 if mode == "hex" else 9
        for k in range(rings):
            pts = []
            scale = min(rect.width, rect.height) * (0.08 + 0.055 * k)
            offset = t * (0.2 + 0.03 * k) if mode == "hex_pulse" else 0
            for j in range(6):
                a = math.tau * j / 6 + offset
                v = bars[(j + k * 5) % n]
                r = scale * (0.7 + 0.55 * v)
                pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
            pygame.draw.polygon(surf, bar_color(theme, k, rings, k / rings, t), pts, 2)

    def _diamonds(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        n = len(bars)
        step = rect.width / max(1, n)
        for i, v in enumerate(bars):
            x = rect.x + i * step + step / 2
            h = max(4, v * rect.height * 0.72)
            w = max(4, step * 0.8)
            pts = [(x, rect.bottom - h), (x + w / 2, rect.bottom - h / 2),
                   (x, rect.bottom), (x - w / 2, rect.bottom - h / 2)]
            if mode == "diamonds_spin":
                ang = t * 1.2 + i * 0.1
                # rotate around x / bottom-ish center only for a subtle skew-like effect
                scale = 0.8 + 0.2 * math.sin(ang)
                pts = [(x + (px - x) * scale, py) for px, py in pts]
            pygame.draw.polygon(surf, bar_color(theme, i, n, v, t), pts, 2)

    def _meter(self, surf, ctx):
        rect, bars, theme, t = self._base(ctx)
        avg = sum(bars) / max(1, len(bars))
        r = int(min(rect.width, rect.height) * (0.18 + avg * 0.25))
        pygame.draw.circle(surf, theme["primary"], rect.center, r, 4)
        for i, v in enumerate(bars[::2]):
            a = -math.pi / 2 + i / max(1, len(bars[::2]) - 1) * math.pi
            rr = min(rect.width, rect.height) * 0.38
            x1 = rect.centerx + math.cos(a) * r
            y1 = rect.centery + math.sin(a) * r
            x2 = rect.centerx + math.cos(a) * (r + v * rr)
            y2 = rect.centery + math.sin(a) * (r + v * rr)
            pygame.draw.line(surf, bar_color(theme, i, len(bars), v, t), (x1, y1), (x2, y2), 3)

    def _gridwave(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        n = len(bars)
        if mode.startswith("stairs"):
            points = []
            for i, v in enumerate(bars):
                x = rect.x + i / n * rect.width
                y = rect.bottom - v * rect.height * 0.9
                points.append((x, y))
            pygame.draw.lines(surf, theme["primary"], False, points, 3)
            if mode == "stairs_mirror":
                pygame.draw.lines(surf, theme["secondary"], False, [(x, 2 * rect.centery - y) for x, y in points], 3)
            return
        for i, v in enumerate(bars):
            a = i / n * math.tau + t * 0.5
            if mode == "vertical_wave":
                x = rect.x + i / n * rect.width
                y = rect.centery + math.sin(a) * rect.height * 0.25 * v
                pygame.draw.line(surf, bar_color(theme, i, n, v, t), (x, rect.centery), (x, y), 3)
            else:
                y = rect.top + i / n * rect.height
                x = rect.centerx + math.sin(a) * rect.width * 0.4 * v
                pygame.draw.line(surf, bar_color(theme, i, n, v, t), (rect.centerx, y), (x, y), 3)

    def _matrix(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        n = max(18, len(bars) // 2)
        for i in range(n):
            x = rect.x + (i + 0.5) * rect.width / n
            v = bars[i % len(bars)]
            length = 4 + int(v * 12)
            for j in range(length):
                y = rect.top + ((i * 97 + j * 31 + int(t * (40 + v * 140))) % max(1, rect.height - 12))
                c = _mix(theme["secondary"], theme["primary"], 1 - j / max(1, length))
                pygame.draw.rect(surf, c, (int(x), int(y), 2, 8))

    def _bars(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        n = len(bars)
        gap = 2 if mode in {"equalizer_wide", "wide_bars", "pillars"} else 4
        width = max(2, (rect.width - gap * (n - 1)) / n)
        for i, v in enumerate(bars):
            h = max(2, int(v * rect.height * 0.92))
            if mode == "pulsing_columns":
                h = max(2, int((v * (0.65 + 0.35 * math.sin(t * 2 + i * 0.1) ** 2)) * rect.height))
            x = rect.x + i * (width + gap)
            y = rect.bottom - h
            col = bar_color(theme, i, n, v, t)
            if mode == "neon_levels":
                layer = pygame.Surface((int(width + 8), int(h + 8)), pygame.SRCALPHA)
                pygame.draw.rect(layer, (*col, 70), (0, 0, int(width + 8), int(h + 8)), border_radius=5)
                pygame.draw.rect(layer, (*col, 255), (4, 4, int(width), int(h)), border_radius=3)
                surf.blit(layer, (int(x - 4), int(y - 4)))
            else:
                pygame.draw.rect(surf, col, (x, y, width, h), border_radius=3)

    def _gear(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        teeth = 18
        base = min(rect.width, rect.height) * (0.18 + sum(bars) / max(1, len(bars)) * 0.12)
        pts = []
        rot = t * (0.25 if mode == "gear" else 0.65)
        for i in range(teeth * 2):
            r = base * (1.18 if i % 2 == 0 else 0.88)
            a = rot + i * math.pi / teeth
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        pygame.draw.polygon(surf, theme["primary"], pts, 3)
        pygame.draw.circle(surf, theme["secondary"], (cx, cy), int(base * 0.28), 4)

    def _vortex(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        n = 140
        for i in range(n):
            a = i * 0.21 + t * (0.4 if mode == "vortex" else -0.7)
            r = 3 + i / n * min(rect.width, rect.height) * 0.46
            v = bars[i % len(bars)]
            a2 = a + v * 0.75
            x = cx + math.cos(a2) * r
            y = cy + math.sin(a2) * r
            c = bar_color(theme, i, n, v, t)
            pygame.draw.circle(surf, c, (int(x), int(y)), 1 + int(v * 3))

    def _mixer(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        n = len(bars)
        cols = max(2, int(math.sqrt(n)))
        rows = math.ceil(n / cols)
        cw = rect.width / cols
        ch = rect.height / rows
        for i, v in enumerate(bars):
            c = i % cols
            r = i // cols
            x = rect.x + c * cw
            y = rect.y + r * ch
            if mode == "mixer_mirror":
                h = v * ch
                y += (ch - h) / 2
            else:
                h = v * ch
            pygame.draw.rect(surf, bar_color(theme, i, n, v, t), (x + 2, y + 2, max(1, cw - 4), max(2, h)), border_radius=2)

    def _scanner(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        x = rect.x + ((math.sin(t * (1.8 if mode == "scanner" else 3.4)) + 1) * 0.5) * rect.width
        pygame.draw.line(surf, theme["primary"], (x, rect.top), (x, rect.bottom), 3)
        n = len(bars)
        radius = 14
        for i, v in enumerate(bars):
            y = rect.top + i / n * rect.height
            d = abs((rect.x + i / n * rect.width) - x)
            glow = max(0.0, 1.0 - d / max(1, rect.width * 0.18)) * max(v, 0.15)
            if glow > 0:
                pygame.draw.circle(surf, bar_color(theme, i, n, glow, t), (int(x), int(y)), int(radius * glow + 2))

    def _drum(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        avg = sum(bars) / max(1, len(bars))
        rings = 7 if mode == "drum" else 12
        for k in range(rings):
            r = (0.08 + k / rings * 0.4) * min(rect.width, rect.height) * (1 + avg * 0.25)
            color = bar_color(theme, k, rings, 1 - k / rings, t)
            pygame.draw.circle(surf, color, (cx, cy), int(r), 2 + (1 if ctx["beat"] and k < 2 else 0))

    def _impulse(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        n = len(bars)
        for i, v in enumerate(bars):
            a = i / n * math.tau - math.pi / 2
            r0 = min(rect.width, rect.height) * 0.08
            r = r0 + v * min(rect.width, rect.height) * (0.38 if mode == "impulse" else 0.52)
            if mode == "impulse_3d":
                r *= 0.7 + 0.3 * math.sin(t * 2 + i * 0.15) ** 2
            p1 = (cx + math.cos(a) * r0, cy + math.sin(a) * r0)
            p2 = (cx + math.cos(a) * r, cy + math.sin(a) * r)
            pygame.draw.line(surf, bar_color(theme, i, n, v, t), p1, p2, 3)

    def _orb(self, surf, ctx):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        avg = sum(bars) / max(1, len(bars))
        r = min(rect.width, rect.height) * (0.12 + avg * 0.3)
        pygame.draw.circle(surf, theme["primary"], (cx, cy), int(r), 4)
        pygame.draw.circle(surf, theme["secondary"], (cx, cy), int(r * 0.52), 3)


def _make_class(index, label, mode):
    return type(
        f"GeneratedVisualizer{index + 1:02d}",
        (AdvancedVisualizer,),
        {"name": label, "preset_name": label, "mode": mode},
    )


GENERATED_VISUALIZERS = [_make_class(i, label, mode) for i, (label, mode) in enumerate(_PRESETS)]
