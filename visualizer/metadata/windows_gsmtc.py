"""Robust Windows GSMTC metadata/timeline reader.

Keeps compatibility with different winsdk builds: optional timeline fields are
read with getattr, while title/artist/duration remain cached through transient
GSMTC failures.
"""
import asyncio
import time

_CACHE = {
    "source": "",
    "artist": "",
    "title": "",
    "duration": 0.0,
    "track_key": "",
    "last_refresh": 0.0,
}

MEDIA_REFRESH_INTERVAL = 0.50


def _seconds(value):
    try:
        return max(0.0, float(value.total_seconds()))
    except Exception:
        return 0.0


def _status_name(status):
    name = getattr(status, "name", None)
    if name:
        return str(name).lower()
    text = str(status or "")
    return text.rsplit(".", 1)[-1].lower()


def _duration_from_timeline(timeline):
    """Get duration without assuming newer optional GSMTC members exist."""
    start = _seconds(getattr(timeline, "start_time", None))
    end = _seconds(getattr(timeline, "end_time", None))
    max_seek = _seconds(getattr(timeline, "max_seek_time", None))

    if end > start:
        return end - start
    if max_seek > start:
        return max_seek - start
    if max_seek > 0.0 and start == 0.0:
        return max_seek
    return 0.0


async def _get_media_info_async():
    from winsdk.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as MediaManager,
    )

    manager = await MediaManager.request_async()
    session = manager.get_current_session()
    if session is None:
        return None

    source = str(getattr(session, "source_app_user_model_id", "") or "")
    timeline = session.get_timeline_properties()

    # Media properties are the only potentially slow/fragile request. Try it,
    # but never let it hide timeline data or cached metadata.
    artist = ""
    title = ""
    try:
        media = await session.try_get_media_properties_async()
        artist = str(getattr(media, "artist", "") or "").strip()
        title = str(getattr(media, "title", "") or "").strip()
    except Exception:
        pass

    position = _seconds(getattr(timeline, "position", None))
    duration = _duration_from_timeline(timeline)

    playback = None
    try:
        playback = session.get_playback_info()
    except Exception:
        pass

    status_name = _status_name(getattr(playback, "playback_status", None)) if playback else ""
    is_playing = status_name in {"playing", "1"}

    rate = 1.0
    try:
        rate = float(getattr(playback, "playback_rate", 1.0) or 1.0)
        if rate <= 0:
            rate = 1.0
    except Exception:
        rate = 1.0

    now = time.monotonic()
    key_candidate = f"{source}|{artist}|{title}" if (artist or title) else ""

    # Update cache only with usable values. A transient empty response must not
    # erase a perfectly valid title or duration from the previous poll.
    if source and source != _CACHE["source"]:
        _CACHE["source"] = source
        _CACHE["artist"] = ""
        _CACHE["title"] = ""
        _CACHE["duration"] = 0.0
        _CACHE["track_key"] = ""

    if artist:
        _CACHE["artist"] = artist
    if title:
        _CACHE["title"] = title

    # Duration normally remains fixed for a track. Grow it when a later poll
    # reveals the actual seek range; never erase it because of a temporary 0.
    if duration > 0:
        if key_candidate and key_candidate != _CACHE["track_key"]:
            _CACHE["duration"] = duration
        else:
            _CACHE["duration"] = max(_CACHE["duration"], duration)

    cached_artist = _CACHE["artist"] or "Nieznany artysta"
    cached_title = _CACHE["title"] or "Nieznany tytul"
    track_key = f"{source}|{cached_artist}|{cached_title}"
    _CACHE["track_key"] = track_key
    _CACHE["last_refresh"] = now

    return {
        "artist": cached_artist,
        "title": cached_title,
        "position": position,
        "duration": _CACHE["duration"],
        "track_key": track_key,
        "source": source,
        "playback_status": status_name,
        "is_playing": is_playing,
        "playback_rate": rate,
        "timeline_start": _seconds(getattr(timeline, "start_time", None)),
        "max_seek": _seconds(getattr(timeline, "max_seek_time", None)),
    }


def available():
    try:
        import winsdk  # noqa: F401
        return True
    except ImportError:
        return False


def get_metadata():
    try:
        return asyncio.run(_get_media_info_async())
    except Exception:
        # Keep the last good values visible even if GSMTC is temporarily busy.
        if _CACHE["artist"] or _CACHE["title"] or _CACHE["duration"] > 0:
            return {
                "artist": _CACHE["artist"] or "Nieznany artysta",
                "title": _CACHE["title"] or "Nieznany tytul",
                "position": 0.0,
                "duration": _CACHE["duration"],
                "track_key": _CACHE["track_key"],
                "source": _CACHE["source"],
                "playback_status": "",
                "is_playing": False,
                "playback_rate": 1.0,
            }
        return None
