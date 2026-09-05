"""Premium audio-reactive visual styles.

Fifty deliberately art-directed presets built from a small set of fast,
composable primitives. The goal is strong silhouettes, restrained motion,
and coherent depth instead of random geometric noise.
"""
import math
import random

import pygame

from ..themes import bar_color, lerp_color
from .base import BaseVisualizer


_PRESETS = [
    ("Aurora Ribbon", "aurora_ribbon"),
    ("Glass Wave", "glass_wave"),
    ("Spectrum Horizon", "spectrum_horizon"),
    ("Prism Wave", "prism_wave"),
    ("Pulse Rail", "pulse_rail"),
    ("Luminous Columns", "luminous_columns"),
    ("Cathedral", "cathedral"),
    ("Monument", "monument"),
    ("Blade Array", "blade_array"),
    ("Pillars Pro", "pillars_pro"),
    ("Orbit Halo", "orbit_halo"),
    ("Planetary", "planetary"),
    ("Solar System", "solar_system"),
    ("Eclipse", "eclipse"),
    ("Saturn", "saturn"),
    ("Pulse Rings", "pulse_rings"),
    ("Ripple Rings", "ripple_rings"),
    ("Concentric Glass", "concentric_glass"),
    ("Core Reactor", "core_reactor"),
    ("Quantum Ring", "quantum_ring"),
    ("Nebula", "nebula"),
    ("Star Drift", "star_drift"),
    ("Comet Field", "comet_field"),
    ("Particle Bloom", "particle_bloom"),
    ("Gravity Well", "gravity_well"),
    ("Kaleido Prime", "kaleido_prime"),
    ("Kaleido Glass", "kaleido_glass"),
    ("Lotus", "lotus"),
    ("Mandala", "mandala"),
    ("Orbit Flower", "orbit_flower"),
    ("Laser Sweep", "laser_sweep"),
    ("Radar Bloom", "radar_bloom"),
    ("Scope", "scope"),
    ("Scanner Grid", "scanner_grid"),
    ("Hologrid", "hologrid"),
    ("Wireframe City", "wireframe_city"),
    ("Tunnel Glass", "tunnel_glass"),
    ("Infinite Hall", "infinite_hall"),
    ("Perspective Grid", "perspective_grid"),
    ("Deep Tunnel", "deep_tunnel"),
    ("Crystal Shards", "crystal_shards"),
    ("Facet", "facet"),
    ("Prism Core", "prism_core"),
    ("Diamond Pulse", "diamond_pulse"),
    ("Fractal Bloom", "fractal_bloom"),
    ("Signal Bloom", "signal_bloom"),
    ("Oscillo Pro", "oscillo_pro"),
    ("Waveform Pro", "waveform_pro"),
    ("Frequency Lens", "frequency_lens"),
    ("Afterglow", "afterglow"),
]


def _mix(a, b, f):
    return lerp_color(a, b, f)


def _clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(v)))


def _glow_line(surf, p1, p2, color, width=2, glow=10):
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    c = (*color, 18)
    pygame.draw.line(layer, c, p1, p2, max(2, glow))
    pygame.draw.line(layer, (*color, 55), p1, p2, max(2, width * 3))
    surf.blit(layer, (0, 0))
    pygame.draw.line(surf, color, p1, p2, width)


def _glow_circle(surf, center, radius, color, width=2, layers=5):
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for k in range(layers, 0, -1):
        alpha = int(8 + 10 * (layers - k) / max(1, layers - 1))
        pygame.draw.circle(layer, (*color, alpha), center, int(radius + k * 4), max(1, width + 1))
    surf.blit(layer, (0, 0))
    pygame.draw.circle(surf, color, center, int(radius), width)


def _point_pairs(points):
    """Return pygame-safe integer (x, y) point pairs."""
    out = []
    for point in points:
        if not isinstance(point, (tuple, list)) or len(point) != 2:
            continue
        try:
            x, y = point
            out.append((int(round(float(x))), int(round(float(y)))))
        except (TypeError, ValueError, OverflowError):
            continue
    return out


def _smooth_points(values, rect, baseline=None, scale=1.0):
    n = len(values)
    if n == 0:
        return []
    y0 = rect.centery if baseline is None else baseline
    out = []
    for i, v in enumerate(values):
        x = rect.x + i * rect.width / max(1, n - 1)
        y = y0 - v * rect.height * 0.42 * scale
        out.append((x, y))
    return out


class AdvancedVisualizer(BaseVisualizer):
    preset_name = "Premium"
    mode = "aurora_ribbon"

    def __init__(self):
        self.phase = random.random() * math.tau
        self.rotation = random.random() * math.tau
        self.seed = random.random() * 1000
        self.stars = [
            (random.random(), random.random(), random.uniform(0.2, 1.0), random.uniform(0.6, 1.8))
            for _ in range(90)
        ]

    def _base(self, ctx):
        rect = ctx["rect"]
        bars = [min(1.0, float(v) * ctx["sensitivity"]) for v in ctx["bars"]]
        theme = ctx["theme"]
        t = ctx["t"]
        return rect, bars, theme, t

    def draw(self, surf, ctx):
        mode = self.mode
        if mode in {"aurora_ribbon", "glass_wave", "spectrum_horizon", "prism_wave", "waveform_pro", "afterglow"}:
            self._wave_family(surf, ctx, mode)
        elif mode in {"pulse_rail", "luminous_columns", "cathedral", "monument", "blade_array", "pillars_pro", "oscillo_pro"}:
            self._column_family(surf, ctx, mode)
        elif mode in {"orbit_halo", "planetary", "solar_system", "eclipse", "saturn"}:
            self._orbital_family(surf, ctx, mode)
        elif mode in {"pulse_rings", "ripple_rings", "concentric_glass", "core_reactor", "quantum_ring"}:
            self._ring_family(surf, ctx, mode)
        elif mode in {"nebula", "star_drift", "comet_field", "particle_bloom", "gravity_well"}:
            self._particle_family(surf, ctx, mode)
        elif mode in {"kaleido_prime", "kaleido_glass", "lotus", "mandala", "orbit_flower", "fractal_bloom"}:
            self._radial_family(surf, ctx, mode)
        elif mode in {"laser_sweep", "radar_bloom", "scope", "scanner_grid", "hologrid"}:
            self._scanner_family(surf, ctx, mode)
        elif mode in {"wireframe_city", "tunnel_glass", "infinite_hall", "perspective_grid", "deep_tunnel"}:
            self._perspective_family(surf, ctx, mode)
        elif mode in {"crystal_shards", "facet", "prism_core", "diamond_pulse"}:
            self._crystal_family(surf, ctx, mode)
        else:
            self._signal_family(surf, ctx, mode)

    def _wave_family(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        wf = ctx["waveform"]
        pts = _smooth_points(wf[::5], rect, scale=1.0 if mode != "afterglow" else 0.75)
        if len(pts) < 2:
            return
        n = len(pts)
        if mode == "aurora_ribbon":
            for off, color_f in ((0, 0.15), (1, 0.52), (-1, 0.85)):
                shifted = [(x, y + off * 9 * (0.7 + 0.3 * math.sin(t))) for x, y in pts]
                c = _mix(theme["primary"], theme["secondary"], color_f)
                pygame.draw.aalines(surf, c, False, shifted)
        elif mode == "glass_wave":
            fill = _point_pairs([(rect.x, rect.centery), *pts, (rect.right, rect.centery)])
            overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            if len(fill) >= 3:
                pygame.draw.polygon(overlay, (*theme["primary"], 28), fill)
            surf.blit(overlay, (0, 0))
            pygame.draw.aalines(surf, theme["secondary"], False, pts)
            pygame.draw.aalines(surf, theme["primary"], False, [(x, 2 * rect.centery - y) for x, y in pts])
        elif mode == "spectrum_horizon":
            base = rect.centery
            for i, v in enumerate(bars):
                x = rect.x + i * rect.width / max(1, len(bars) - 1)
                h = 4 + v * rect.height * 0.32
                c = bar_color(theme, i, len(bars), v, t)
                pygame.draw.line(surf, c, (x, base - h), (x, base + h), 2)
            pygame.draw.aaline(surf, theme["secondary"], pts[0], pts[-1])
        elif mode == "prism_wave":
            for j, c in enumerate((theme["primary"], theme["secondary"], _mix(theme["primary"], theme["secondary"], 0.5))):
                shifted = [(x, y + (j - 1) * 10) for x, y in pts]
                pygame.draw.aalines(surf, c, False, shifted)
        elif mode == "afterglow":
            for k in range(5, 0, -1):
                alpha = int(12 + k * 5)
                layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
                shifted = [(x, y + math.sin(t * 2.0 + i * 0.08) * k * 2) for i, (x, y) in enumerate(pts)]
                pygame.draw.aalines(layer, (*theme["primary"], alpha), False, shifted)
                surf.blit(layer, (0, 0))
            pygame.draw.aalines(surf, theme["secondary"], False, pts)
        else:
            pygame.draw.aalines(surf, theme["primary"], False, pts)
            mirror = [(x, 2 * rect.centery - y) for x, y in pts]
            pygame.draw.aalines(surf, theme["secondary"], False, mirror)

    def _column_family(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        n = len(bars)
        if not n:
            return
        gap = 4 if mode in {"pillars_pro", "luminous_columns"} else 3
        width = max(2, (rect.width - gap * (n - 1)) / n)
        center = rect.centerx
        for i, v in enumerate(bars):
            x = rect.x + i * (width + gap)
            h = 4 + v * rect.height * (0.78 if mode not in {"cathedral", "monument"} else 0.62)
            col = bar_color(theme, i, n, v, t)
            if mode == "cathedral":
                h *= 0.75 + 0.25 * (1 - abs(i - n / 2) / max(1, n / 2))
            if mode == "monument":
                h *= 0.6 + 0.4 * math.sin((i / max(1, n - 1)) * math.pi)
            if mode == "blade_array":
                lean = (v - 0.5) * 14
                pygame.draw.polygon(surf, col, _point_pairs([(x + width / 2, rect.bottom - h), (x + width + lean, rect.bottom), (x, rect.bottom)]), 2)
                continue
            if mode == "oscillo_pro":
                y0 = rect.centery
                hh = h * 0.55
                pygame.draw.line(surf, col, (x + width / 2, y0 - hh), (x + width / 2, y0 + hh), 2)
                continue
            if mode == "pulse_rail":
                y = rect.bottom - h
                pygame.draw.line(surf, col, (x + width / 2, y), (x + width / 2, rect.bottom), 1)
                pygame.draw.circle(surf, col, (int(x + width / 2), int(y)), 2 + int(v * 4))
                continue
            if mode == "monument":
                pygame.draw.rect(surf, col, (x, rect.bottom - h, width, h), border_radius=2)
                pygame.draw.line(surf, theme["secondary"], (x, rect.bottom - h), (x + width, rect.bottom - h), 2)
                continue
            if mode == "luminous_columns":
                # One reusable glow surface per frame instead of allocating a
                # full-screen surface for every single column. This was the
                # main source of frame drops with 48+ bars.
                pass
            pygame.draw.rect(surf, col, (x, rect.bottom - h, width, h), border_radius=3)
            if mode == "cathedral":
                pygame.draw.line(surf, _mix(col, theme["bg"], 0.35), (x, rect.bottom - h), (x + width, rect.bottom - h), 2)
        if mode == "luminous_columns":
            # Draw all glows in a single alpha layer. The old implementation
            # created one full-size Surface per bar per frame (e.g. ~48
            # allocations every frame at 60 FPS).
            glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for i, v in enumerate(bars):
                if v < 0.04:
                    continue
                x = rect.x + i * (width + gap)
                h = 4 + v * rect.height * 0.78
                col = bar_color(theme, i, n, v, t)
                alpha = int(8 + min(28, v * 22))
                pygame.draw.rect(
                    glow,
                    (*col, alpha),
                    (max(rect.left, x - 2), rect.bottom - h, min(rect.right - x + 2, width + 4), h),
                    border_radius=4,
                )
            surf.blit(glow, (0, 0))

        if mode == "pillars_pro":
            pygame.draw.line(surf, _mix(theme["secondary"], theme["bg"], 0.45), (rect.left, rect.bottom - 1), (rect.right, rect.bottom - 1), 2)

    def _orbital_family(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        m = min(rect.width, rect.height)
        avg = sum(bars) / max(1, len(bars))
        core = int(m * (0.055 + avg * 0.035))
        _glow_circle(surf, (cx, cy), core, theme["secondary"], 3, 4)
        rings = 3 if mode in {"eclipse", "saturn"} else 5
        for k in range(rings):
            r = m * (0.12 + 0.10 * k) * (1 + avg * 0.16)
            col = _mix(theme["primary"], theme["secondary"], k / max(1, rings - 1))
            pygame.draw.ellipse(surf, col, (cx - r, cy - r * 0.52, 2 * r, r * 1.04), 1)
        if mode == "eclipse":
            pygame.draw.circle(surf, theme["bg"], (cx - int(m * 0.075), cy), int(m * 0.11))
            pygame.draw.circle(surf, theme["primary"], (cx - int(m * 0.075), cy), int(m * 0.11), 2)
        elif mode == "saturn":
            r = m * 0.16
            pygame.draw.ellipse(surf, theme["secondary"], (cx - r * 1.8, cy - r * 0.45, r * 3.6, r * 0.9), 2)
        count = 8 if mode != "solar_system" else 12
        for i in range(count):
            a = self.rotation + t * (0.15 + i * 0.01) + i * math.tau / count
            radius = m * (0.12 + (i + 1) / count * 0.32)
            x = cx + math.cos(a) * radius
            y = cy + math.sin(a) * radius * 0.52
            v = bars[i % len(bars)] if bars else 0
            c = bar_color(theme, i, count, v, t)
            pygame.draw.circle(surf, c, (int(x), int(y)), 2 + int(v * 3))

    def _ring_family(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        m = min(rect.width, rect.height)
        avg = sum(bars) / max(1, len(bars))
        if mode == "core_reactor":
            for k in range(7):
                r = m * (0.05 + 0.035 * k) * (0.95 + avg * 0.35)
                c = bar_color(theme, k, 7, avg, t)
                _glow_circle(surf, (cx, cy), r, c, 1 if k > 2 else 2, 3)
        elif mode == "quantum_ring":
            for i, v in enumerate(bars[::2]):
                a = i / max(1, len(bars[::2])) * math.tau + t * 0.35
                r = m * (0.20 + 0.22 * v)
                p = (cx + math.cos(a) * r, cy + math.sin(a) * r)
                pygame.draw.circle(surf, bar_color(theme, i, len(bars), v, t), (int(p[0]), int(p[1])), 2 + int(v * 3))
        else:
            count = 9 if mode == "ripple_rings" else 6
            for k in range(count):
                phase = (t * (0.22 if mode != "ripple_rings" else 0.48) + k / count) % 1.0
                r = m * (0.04 + phase * 0.42) * (1 + avg * 0.18)
                alpha = int(230 * (1 - phase))
                c = bar_color(theme, k, count, 1 - phase, t)
                layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
                pygame.draw.circle(layer, (*c, max(20, alpha)), (cx, cy), int(r), 2)
                surf.blit(layer, (0, 0))
            if mode == "concentric_glass":
                _glow_circle(surf, (cx, cy), m * (0.10 + avg * 0.10), theme["secondary"], 3, 4)

    def _particle_family(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        avg = sum(bars) / max(1, len(bars))
        count = 70 if mode != "nebula" else 95
        for i in range(count):
            u = (i * 0.61803398875 + self.seed) % 1.0
            v = (i * 0.41421356237 + self.seed * 0.37) % 1.0
            a = u * math.tau + t * (0.10 + v * 0.18)
            radius = (0.08 + v * 0.43) * min(rect.width, rect.height)
            if mode == "gravity_well":
                radius *= 0.78 + 0.22 * math.cos(t + i * 0.23)
            x = cx + math.cos(a) * radius
            y = cy + math.sin(a) * radius * 0.68
            idx = i % max(1, len(bars))
            amp = bars[idx] if bars else avg
            if mode == "comet_field" and i % 7 == 0:
                prev = (x - math.cos(a) * (8 + amp * 30), y - math.sin(a) * (8 + amp * 30))
                pygame.draw.line(surf, theme["secondary"], prev, (x, y), 1)
            if mode == "nebula":
                size = 1 + int(amp * 3)
            elif mode == "particle_bloom":
                size = 1 + int(amp * 5)
            else:
                size = 1 + int(amp * 3)
            pygame.draw.circle(surf, bar_color(theme, idx, max(1, len(bars)), amp, t), (int(x), int(y)), size)
        _glow_circle(surf, (cx, cy), min(rect.width, rect.height) * (0.035 + avg * 0.05), theme["primary"], 2, 4)

    def _radial_family(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        n = len(bars)
        m = min(rect.width, rect.height)
        spokes = 64 if mode in {"mandala", "fractal_bloom"} else 42
        points = []
        for i in range(spokes + 1):
            a = i / spokes * math.tau + self.rotation + t * 0.12
            v = bars[(i * 3) % n] if n else 0
            if mode == "lotus":
                r = m * (0.11 + 0.16 * v) * (1 + 0.12 * math.sin(i * 0.7))
            elif mode == "orbit_flower":
                r = m * (0.10 + 0.22 * (0.4 + 0.6 * v))
            else:
                r = m * (0.10 + 0.22 * v)
            points.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        for k, radius in enumerate((0.15, 0.24, 0.32)):
            pygame.draw.circle(surf, _mix(theme["primary"], theme["secondary"], k / 3), (cx, cy), int(m * radius), 1)
        pygame.draw.aalines(surf, theme["primary"], True, points)
        if mode in {"kaleido_prime", "kaleido_glass"}:
            mirror = [(2 * cx - x, y) for x, y in points]
            pygame.draw.aalines(surf, theme["secondary"], True, mirror)
        elif mode == "mandala":
            for shift in range(6):
                a = shift * math.tau / 6 + t * 0.1
                dx, dy = math.cos(a) * m * 0.18, math.sin(a) * m * 0.18
                pygame.draw.circle(surf, theme["secondary"], (int(cx + dx), int(cy + dy)), int(m * 0.06), 1)

    def _scanner_family(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        sweep = (t * (1.1 if mode != "scope" else 0.55) + self.phase) % math.tau
        r = min(rect.width, rect.height) * 0.40
        if mode == "scanner_grid" or mode == "hologrid":
            for i in range(8):
                y = rect.top + i * rect.height / 8
                pygame.draw.line(surf, _mix(theme["primary"], theme["bg"], 0.65), (rect.left, y), (rect.right, y), 1)
                x = rect.left + i * rect.width / 8
                pygame.draw.line(surf, _mix(theme["secondary"], theme["bg"], 0.7), (x, rect.top), (x, rect.bottom), 1)
        ex = cx + math.cos(sweep) * r
        ey = cy + math.sin(sweep) * r
        _glow_line(surf, (cx, cy), (ex, ey), theme["primary"], 2, 12)
        for i, v in enumerate(bars[::2]):
            a = i * 2 / max(1, len(bars) - 1) * math.tau
            rr = r * (0.18 + 0.72 * v)
            x = cx + math.cos(a) * rr
            y = cy + math.sin(a) * rr
            c = bar_color(theme, i, max(1, len(bars)), v, t)
            if mode == "radar_bloom":
                pygame.draw.circle(surf, c, (int(x), int(y)), 2 + int(v * 5))
            else:
                pygame.draw.circle(surf, c, (int(x), int(y)), 2)
        pygame.draw.circle(surf, _mix(theme["primary"], theme["bg"], 0.35), (cx, cy), int(r), 1)

    def _perspective_family(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx = rect.centerx
        horizon = rect.top + rect.height * 0.42
        base = rect.bottom
        for k in range(9):
            p = (k / 9 + t * 0.08) % 1.0
            y = horizon + (p ** 1.8) * (base - horizon)
            col = _mix(theme["primary"], theme["bg"], 0.25 + p * 0.55)
            pygame.draw.line(surf, col, (rect.left, y), (rect.right, y), 1)
        spokes = 12
        for i in range(spokes):
            x = rect.left + (i / (spokes - 1)) * rect.width
            col = _mix(theme["secondary"], theme["bg"], 0.35)
            pygame.draw.line(surf, col, (cx, horizon), (x, base), 1)
        if mode == "wireframe_city":
            for i in range(12):
                x = rect.left + i * rect.width / 12
                v = bars[i % len(bars)] if bars else 0
                h = 20 + v * rect.height * 0.35
                pygame.draw.rect(surf, bar_color(theme, i, 12, v, t), (x, horizon - h, rect.width / 18, h), 1)
        elif mode in {"tunnel_glass", "infinite_hall", "deep_tunnel"}:
            for k in range(11):
                p = (k / 11 + t * (0.18 if mode != "deep_tunnel" else 0.28)) % 1.0
                w = rect.width * (0.07 + p * 0.86)
                h = rect.height * (0.05 + p * 0.62)
                col = bar_color(theme, k, 11, 1 - p, t)
                pygame.draw.rect(surf, col, (cx - w / 2, horizon - h / 2, w, h), 1)

    def _crystal_family(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        cx, cy = rect.center
        n = len(bars)
        m = min(rect.width, rect.height)
        for i, v in enumerate(bars):
            a = i / max(1, n) * math.tau + self.rotation * 0.15
            r0 = m * 0.10
            r1 = r0 + m * (0.14 + 0.22 * v)
            w = m * (0.012 + 0.028 * v)
            p1 = (cx + math.cos(a) * r0, cy + math.sin(a) * r0)
            p2 = (cx + math.cos(a) * r1, cy + math.sin(a) * r1)
            c = bar_color(theme, i, n, v, t)
            if mode == "facet":
                pygame.draw.polygon(surf, c, _point_pairs([p1, (p2[0] + w, p2[1]), (cx + math.cos(a + 0.18) * r1, cy + math.sin(a + 0.18) * r1)]), 1)
            elif mode == "prism_core":
                pygame.draw.line(surf, c, p1, p2, 2)
                if i % 3 == 0:
                    pygame.draw.circle(surf, theme["secondary"], (int(p2[0]), int(p2[1])), 2)
            else:
                pts = [p1, (cx + math.cos(a - 0.10) * r1, cy + math.sin(a - 0.10) * r1),
                       p2, (cx + math.cos(a + 0.10) * r1, cy + math.sin(a + 0.10) * r1)]
                pygame.draw.polygon(surf, c, [(int(x), int(y)) for x, y in pts], 1)
        if mode == "diamond_pulse":
            _glow_circle(surf, (cx, cy), m * (0.07 + sum(bars) / max(1, n) * 0.06), theme["secondary"], 2, 4)

    def _signal_family(self, surf, ctx, mode):
        rect, bars, theme, t = self._base(ctx)
        n = len(bars)
        cx, cy = rect.center
        lens = min(rect.width, rect.height) * 0.34
        if mode == "signal_bloom":
            for ring in range(6):
                r = lens * (0.18 + ring * 0.13) * (0.92 + 0.12 * math.sin(t * 1.8 + ring))
                c = bar_color(theme, ring, 6, sum(bars) / max(1, n), t)
                pygame.draw.circle(surf, c, (cx, cy), int(r), 2)
        else:
            for i, v in enumerate(bars):
                a = i / max(1, n) * math.tau + t * 0.25
                r = lens * (0.12 + v * 0.85)
                x = cx + math.cos(a) * r
                y = cy + math.sin(a) * r
                c = bar_color(theme, i, n, v, t)
                pygame.draw.line(surf, c, (cx, cy), (x, y), 2)
            _glow_circle(surf, (cx, cy), lens * 0.08, theme["primary"], 2, 4)
        if mode == "frequency_lens":
            pygame.draw.circle(surf, theme["secondary"], (cx, cy), int(lens * 0.62), 2)
            pygame.draw.circle(surf, theme["primary"], (cx, cy), int(lens * 0.22), 1)


def _make_class(index, label, mode):
    return type(
        f"PremiumVisualizer{index + 1:02d}",
        (AdvancedVisualizer,),
        {"name": label, "preset_name": label, "mode": mode},
    )


GENERATED_VISUALIZERS = [_make_class(i, label, mode) for i, (label, mode) in enumerate(_PRESETS)]
