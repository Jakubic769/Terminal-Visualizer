"""Reads artist/title/position/duration from whatever MPRIS-compatible
player is active (Spotify, VLC, browsers, rhythmbox, mpv w/ mpris plugin,
...) via the `playerctl` CLI tool."""
import shutil
import subprocess

_SEP = "\u0001"


def available():
    return shutil.which("playerctl") is not None


def get_metadata():
    if not available():
        return None
    try:
        fmt = _SEP.join(["{{artist}}", "{{title}}", "{{mpris:length}}"])
        out = subprocess.run(
            ["playerctl", "metadata", "--format", fmt],
            capture_output=True, text=True, timeout=1,
        ).stdout.strip()
        if not out:
            return None
        parts = out.split(_SEP)
        if len(parts) != 3:
            return None
        artist, title, length_us = parts

        pos_out = subprocess.run(
            ["playerctl", "position"], capture_output=True, text=True, timeout=1,
        ).stdout.strip()
        position = float(pos_out) if pos_out else 0.0
        duration = float(length_us) / 1_000_000 if length_us else 0.0

        return {
            "artist": artist or "Nieznany artysta",
            "title": title or "Nieznany tytul",
            "position": max(position, 0.0),
            "duration": max(duration, 0.0),
        }
    except (subprocess.SubprocessError, ValueError, OSError):
        return None
