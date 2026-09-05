"""Color themes for the visualizer.

Every theme is a dict with:
  bg        - background color (r,g,b)
  primary   - main accent color (r,g,b)
  secondary - second color, used for gradients
  text      - text color for the bottom info bar
  dynamic   - if True, `primary`/`secondary` are ignored and colors are
              generated procedurally each frame (rainbow / hue-rotate).
"""
import colorsys

THEMES = {
    "cava_green": {
        "label": "Cava Green",
        "bg": (8, 10, 10),
        "primary": (0, 255, 130),
        "secondary": (0, 150, 255),
        "text": (230, 255, 240),
    },
    "neon_purple": {
        "label": "Neon Purple",
        "bg": (10, 6, 16),
        "primary": (200, 60, 255),
        "secondary": (60, 200, 255),
        "text": (240, 230, 255),
    },
    "fire": {
        "label": "Fire",
        "bg": (12, 6, 4),
        "primary": (255, 90, 0),
        "secondary": (255, 220, 0),
        "text": (255, 230, 200),
    },
    "ocean": {
        "label": "Ocean",
        "bg": (4, 10, 16),
        "primary": (0, 180, 255),
        "secondary": (0, 255, 200),
        "text": (220, 245, 255),
    },
    "synthwave": {
        "label": "Synthwave",
        "bg": (16, 4, 24),
        "primary": (255, 0, 150),
        "secondary": (0, 220, 255),
        "text": (255, 220, 255),
    },
    "mono_white": {
        "label": "Mono White",
        "bg": (6, 6, 6),
        "primary": (235, 235, 235),
        "secondary": (140, 140, 140),
        "text": (255, 255, 255),
    },
    "blood": {
        "label": "Blood",
        "bg": (8, 2, 2),
        "primary": (220, 0, 30),
        "secondary": (255, 120, 0),
        "text": (255, 220, 220),
    },
    "rainbow": {
        "label": "Rainbow (dynamic)",
        "dynamic": True,
        "bg": (6, 6, 8),
        "text": (255, 255, 255),
    },
}

THEME_ORDER = list(THEMES.keys())


def make_custom_theme(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    h2 = (h + 0.5) % 1.0
    sr, sg, sb = colorsys.hsv_to_rgb(h2, min(s, 0.9), 1.0)
    return {
        "label": "Custom",
        "bg": (6, 6, 8),
        "primary": (r, g, b),
        "secondary": (int(sr * 255), int(sg * 255), int(sb * 255)),
        "text": (245, 245, 245),
    }


def hue(t, s=0.85, v=1.0):
    """t in [0,1) -> (r,g,b) 0-255, for rainbow / dynamic themes."""
    r, g, b = colorsys.hsv_to_rgb(t % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def lerp_color(c1, c2, f):
    f = max(0.0, min(1.0, f))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * f) for i in range(3))


def bar_color(theme, index, n, value, t):
    """Return the color to use for bar/element `index` of `n`, given its
    current amplitude `value` (0..1) and elapsed time `t` (for dynamic themes)."""
    if theme.get("dynamic"):
        return hue(t * 0.08 + index / max(n, 1))
    lo = theme["primary"]
    hi = theme["secondary"]
    return lerp_color(lo, hi, value)
