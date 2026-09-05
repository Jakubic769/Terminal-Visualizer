import pygame

from .base import BaseVisualizer


class VuMeterVisualizer(BaseVisualizer):
    name = "VU Metr"

    def __init__(self):
        self.peak_l = 0.0
        self.peak_r = 0.0

    def draw(self, surf, ctx):
        rect = ctx["rect"]
        theme = ctx["theme"]
        left, right = ctx["stereo_rms"]
        left = min(1.0, left * ctx["sensitivity"] * 1.6)
        right = min(1.0, right * ctx["sensitivity"] * 1.6)
        dt = ctx["dt"]

        self.peak_l = max(left, self.peak_l - dt * 0.5)
        self.peak_r = max(right, self.peak_r - dt * 0.5)

        pad = rect.width * 0.12
        bar_w = (rect.width - pad * 3) / 2
        bottom = rect.bottom - 10
        top = rect.top + 10
        full_h = bottom - top

        for label_x, value, peak in (
            (rect.x + pad, left, self.peak_l),
            (rect.x + pad * 2 + bar_w, right, self.peak_r),
        ):
            pygame.draw.rect(surf, tuple(int(c * 0.18) for c in theme["primary"]),
                              (label_x, top, bar_w, full_h), border_radius=6)
            h = value * full_h
            # segmented look: green -> yellow -> red zones, tinted by theme
            n_segments = 24
            seg_h = full_h / n_segments
            lit = int(value * n_segments)
            for s in range(n_segments):
                frac = s / n_segments
                if frac < 0.6:
                    color = theme["primary"]
                elif frac < 0.85:
                    color = _mix(theme["primary"], (255, 210, 0), 0.6)
                else:
                    color = (235, 40, 40)
                y = bottom - (s + 1) * seg_h
                alpha_on = s < lit
                col = color if alpha_on else tuple(int(c * 0.15) for c in color)
                pygame.draw.rect(surf, col, (label_x + 3, y + 2, bar_w - 6, seg_h - 3), border_radius=2)

            peak_y = bottom - peak * full_h
            pygame.draw.rect(surf, theme.get("text", (255, 255, 255)), (label_x, peak_y - 2, bar_w, 3))


def _mix(a, b, f):
    return tuple(int(a[i] * (1 - f) + b[i] * f) for i in range(3))
