"""Windows GSMTC metadata reader with cached media identity and a smooth timeline.

GSMTC exposes media properties separately from the timeline. Some applications
(such as Spotify/Edge) can temporarily fail or return incomplete media
properties while the timeline remains valid, so the reader keeps the last good
artist/title/duration and only refreshes them when needed.
"""
import asyncio
from datetime import timezone
import time


_CACHE = {
    "source": "",
    "track_key": "",
    "artist": "",
    "title": "",
    "duration": 0.0,
    "last_media_refresh": 0.0,
}

MEDIA_REFRESH_INTERVAL = 0.75


def _seconds(value):
    try:
        return max(0.0, float(value.total_seconds()))
    except Exception:
        return 0.0


def _timestamp_seconds(value):
    """Convert WinRT DateTimeOffset-like value to POSIX seconds when possible."""
    if value is None:
        return None
    try:
        return value.timestamp()
    except Exception:
        pass
    try:
        if getattr(value, "tzinfo", None) is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).timestamp()
    except Exception:
        return None


async def _get_current_session():
    from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
    manager = await MediaManager.request_async()
    return manager.get_current_session()


async def _get_media_properties(session):
    return await session.try_get_media_properties_async()


def _duration_from_timeline(timeline):
    start = _seconds(timeline.start_time)
    end = _seconds(timeline.end_time)
    max_seek = _seconds(timeline.max_seek_time)
    candidates = []
    if end > start:
        candidates.append(end - start)
    if max_seek > start:
        candidates.append(max_seek - start)
    if max_seek > 0.0 and start == 0.0:
        candidates.append(max_seek)
    return max(candidates, default=0.0)


async def _get_media_info_async():
    from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus

    session = await _get_current_session()
    if session is None:
        return None

    timeline = session.get_timeline_properties()
    playback = session.get_playback_info()
    source = session.source_app_user_model_id or ""

    # Timeline reads are synchronous and cheap. Media properties are remote/
    # async and occasionally fail while apps are changing tracks, so refresh
    # them independently and retain the previous good values on failure.
    now = time.monotonic()
    try:
        candidate_duration = _duration_from_timeline(timeline)
    except Exception:
        candidate_duration = 0.0

    media_needs_refresh = (
        source != _CACHE["source"]
        or not _CACHE["title"]
        or (now - _CACHE["last_media_refresh"] >= MEDIA_REFRESH_INTERVAL)
    )

    if media_needs_refresh:
        try:
            info = await _get_media_properties(session)
            artist = (getattr(info, "artist", None) or "").strip()
            title = (getattr(info, "title", None) or "").strip()
            _CACHE["source"] = source
            if artist or title:
                _CACHE["artist"] = artist or "Nieznany artysta"
                _CACHE["title"] = title or "Nieznany tytul"
            if candidate_duration > 0.0:
                _CACHE["duration"] = max(_CACHE["duration"], candidate_duration)
        except Exception:
            # Keep the old metadata. A transient GSMTC media-properties failure
            # must never make the title disappear from the UI.
            _CACHE["source"] = source
        finally:
            _CACHE["last_media_refresh"] = now

    if candidate_duration > 0.0:
        # Duration should only grow during the life of a track. This prevents a
        # temporary zero/short browser timeline from wiping an already-known
        # duration.
        _CACHE["duration"] = max(_CACHE["duration"], candidate_duration)

    start = _seconds(timeline.start_time)
    position = _seconds(timeline.position)
    min_seek = _seconds(timeline.min_seek_time)
    max_seek = _seconds(timeline.max_seek_time)
    duration = _CACHE["duration"]

    status = playback.playback_status
    status_name = getattr(status, "name", "") or str(status).split(".")[-1]
    is_playing = status == PlaybackStatus.playing or status_name.lower() == "playing"

    playback_rate = 1.0
    try:
        playback_rate = float(playback.playback_rate)
        if playback_rate <= 0.0:
            playback_rate = 1.0
    except Exception:
        pass

    updated_at = _timestamp_seconds(getattr(timeline, "last_updated_time", None))
    artist = _CACHE["artist"] or "Nieznany artysta"
    title = _CACHE["title"] or "Nieznany tytul"
    track_key = f"{source}|{artist}|{title}"

    # Position is already reported in the media timeline coordinate system.
    # Keep it as-is; MinSeekTime is a seek boundary, not a value to subtract.
    position = max(position, 0.0)
    if duration > 0.0:
        position = min(position, duration)

    return {
        "artist": artist,
        "title": title,
        "position": position,
        "duration": duration,
        "track_key": track_key,
        "source": source,
        "playback_status": status_name.lower(),
        "is_playing": is_playing,
        "playback_rate": playback_rate,
        "timeline_updated_at": updated_at,
        "min_seek": min_seek,
        "max_seek": max_seek,
        "timeline_start": start,
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
        # Do not poison the UI with an exception when GSMTC is temporarily
        # unavailable. The MetadataWorker will simply keep its last clock.
        return None
