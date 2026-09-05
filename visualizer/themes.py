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

EXTRA_THEMES = {
    "midnight_blue": {"label": "Midnight Blue", "bg": (3, 8, 22), "primary": (36, 110, 255), "secondary": (0, 230, 255), "text": (245,245,245)},
    "ice": {"label": "Ice", "bg": (5, 14, 20), "primary": (110, 240, 255), "secondary": (210, 255, 255), "text": (245,245,245)},
    "aurora": {"label": "Aurora", "bg": (4, 18, 14), "primary": (0, 255, 170), "secondary": (150, 90, 255), "text": (245,245,245)},
    "lime": {"label": "Lime", "bg": (8, 18, 4), "primary": (160, 255, 0), "secondary": (40, 220, 110), "text": (245,245,245)},
    "mint": {"label": "Mint", "bg": (4, 18, 15), "primary": (80, 255, 190), "secondary": (0, 170, 140), "text": (245,245,245)},
    "turquoise": {"label": "Turquoise", "bg": (3, 18, 20), "primary": (0, 255, 230), "secondary": (0, 120, 255), "text": (245,245,245)},
    "sky": {"label": "Sky", "bg": (4, 12, 25), "primary": (80, 190, 255), "secondary": (180, 240, 255), "text": (245,245,245)},
    "royal": {"label": "Royal", "bg": (8, 5, 25), "primary": (90, 80, 255), "secondary": (220, 80, 255), "text": (245,245,245)},
    "violet": {"label": "Violet", "bg": (15, 4, 25), "primary": (170, 70, 255), "secondary": (255, 100, 220), "text": (245,245,245)},
    "magenta": {"label": "Magenta", "bg": (24, 3, 18), "primary": (255, 50, 190), "secondary": (255, 120, 255), "text": (245,245,245)},
    "pink": {"label": "Pink", "bg": (24, 5, 15), "primary": (255, 80, 170), "secondary": (255, 210, 245), "text": (245,245,245)},
    "rose": {"label": "Rose", "bg": (25, 5, 8), "primary": (255, 60, 100), "secondary": (255, 170, 200), "text": (245,245,245)},
    "coral": {"label": "Coral", "bg": (25, 8, 5), "primary": (255, 110, 90), "secondary": (255, 220, 100), "text": (245,245,245)},
    "amber": {"label": "Amber", "bg": (24, 12, 3), "primary": (255, 175, 40), "secondary": (255, 245, 120), "text": (245,245,245)},
    "gold": {"label": "Gold", "bg": (22, 15, 3), "primary": (255, 205, 40), "secondary": (255, 255, 170), "text": (245,245,245)},
    "lemon": {"label": "Lemon", "bg": (17, 20, 2), "primary": (230, 255, 40), "secondary": (255, 255, 150), "text": (245,245,245)},
    "electric_blue": {"label": "Electric Blue", "bg": (2, 8, 25), "primary": (50, 120, 255), "secondary": (80, 245, 255), "text": (245,245,245)},
    "deep_ocean": {"label": "Deep Ocean", "bg": (2, 8, 17), "primary": (0, 90, 220), "secondary": (0, 220, 180), "text": (245,245,245)},
    "teal": {"label": "Teal", "bg": (2, 18, 18), "primary": (0, 220, 190), "secondary": (120, 255, 220), "text": (245,245,245)},
    "forest": {"label": "Forest", "bg": (3, 14, 5), "primary": (40, 220, 90), "secondary": (180, 255, 100), "text": (245,245,245)},
    "emerald": {"label": "Emerald", "bg": (2, 18, 10), "primary": (0, 210, 110), "secondary": (80, 255, 170), "text": (245,245,245)},
    "violet_fire": {"label": "Violet Fire", "bg": (18, 4, 20), "primary": (180, 0, 255), "secondary": (255, 100, 40), "text": (245,245,245)},
    "plasma": {"label": "Plasma", "bg": (10, 2, 24), "primary": (255, 30, 220), "secondary": (80, 120, 255), "text": (245,245,245)},
    "white_gold": {"label": "White Gold", "bg": (12, 12, 10), "primary": (255, 245, 200), "secondary": (255, 170, 60), "text": (245,245,245)},
    "silver_blue": {"label": "Silver Blue", "bg": (8, 10, 15), "primary": (200, 220, 255), "secondary": (90, 150, 255), "text": (245,245,245)},
}

THEMES.update(EXTRA_THEMES)

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


def normalize_theme(theme):
    """Return a complete, safe theme dict.

    Some built-in/dynamic themes intentionally omit accent colors, and older
    saved configurations may contain incomplete custom themes. All
    visualizers should nevertheless receive the same complete schema.
    """
    safe = dict(theme or {})
    safe.setdefault("label", "Custom")
    safe.setdefault("bg", (6, 6, 8))
    safe.setdefault("primary", (235, 235, 235))
    safe.setdefault("secondary", (140, 140, 140))
    safe.setdefault("text", (255, 255, 255))
    safe.setdefault("dynamic", False)
    return safe


def bar_color(theme, index, n, value, t):
    """Return the color to use for bar/element `index` of `n`, given its
    current amplitude `value` (0..1) and elapsed time `t` (for dynamic themes)."""
    theme = normalize_theme(theme)
    if theme.get("dynamic"):
        return hue(t * 0.08 + index / max(n, 1))
    lo = theme["primary"]
    hi = theme["secondary"]
    return lerp_color(lo, hi, value)
