import json
import os
import sys


def config_dir():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    d = os.path.join(base, "visualizer")
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass
    return d


def config_path():
    return os.path.join(config_dir(), "config.json")


DEFAULTS = {
    "style_index": 0,
    "theme": "cava_green",
    "custom_color": None,   # [r,g,b] or None
    "sensitivity": 1.0,
    "n_bars": 48,
    "fps": 60,
    "fullscreen": False,
    "transparency_enabled": False,
    "transparency_sensitivity": 1.0,
}


def load():
    cfg = dict(DEFAULTS)
    try:
        with open(config_path(), "r", encoding="utf-8") as f:
            saved = json.load(f)
        cfg.update({k: v for k, v in saved.items() if k in DEFAULTS})
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return cfg


def save(cfg):
    try:
        with open(config_path(), "w", encoding="utf-8") as f:
            json.dump({k: cfg.get(k, v) for k, v in DEFAULTS.items()}, f, indent=2)
    except OSError:
        pass
