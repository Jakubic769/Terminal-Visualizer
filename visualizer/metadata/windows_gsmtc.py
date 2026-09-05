"""Robust Windows GSMTC metadata reader.

Uses Windows GlobalSystemMediaTransportControlsSession for title/artist and
playback timeline. Timeline position is extrapolated from LastUpdatedTime and
PlaybackRate, while duration prefers MaxSeekTime as a browser-friendly
fallback when EndTime/StartTime are temporarily incomplete.
"""
import asyncio
from datetime import datetime, timezone


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
        # Some projections expose datetime-ish objects without timestamp().
        if getattr(value, "tzinfo", None) is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).timestamp()
    except Exception:
        return None


async def _get_media_info_async():
    from winsdk.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as MediaManager,
        GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
    )

    manager = await MediaManager.request_async()
    session = manager.get_current_session()
    if session is None:
        return None

    info = await session.try_get_media_properties_async()
    timeline = session.get_timeline_properties()
    playback = session.get_playback_info()

    start = _seconds(timeline.start_time)
    end = _seconds(timeline.end_time)
    position = _seconds(timeline.position)
    max_seek = _seconds(timeline.max_seek_time)
    min_seek = _seconds(timeline.min_seek_time)

    # GSMTC exposes EndTime as an absolute timeline endpoint. In browsers
    # (notably Edge/Chromium media sessions) it can temporarily be missing,
    # while MaxSeekTime already contains the useful media length.
    duration_candidates = []
    if end > start:
        duration_candidates.append(end - start)
    if max_seek > start:
        duration_candidates.append(max_seek - start)
    if max_seek > 0.0 and start == 0.0:
        duration_candidates.append(max_seek)
    duration = max(duration_candidates, default=0.0)

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

    artist = info.artist or "Nieznany artysta"
    title = info.title or "Nieznany tytul"
    source = session.source_app_user_model_id or ""

    # Do not include timeline timestamps in the key: Spotify/GSMTC can refresh
    # these while the same track is still playing.
    # Position is already the playback position of the current media item;
    # do not subtract MinSeekTime here. MinSeekTime is a seek-range boundary,
    # not an offset that should be applied to the displayed clock.
    position = max(position, 0.0)
    return {
        "artist": artist,
        "title": title,
        "position": min(position, duration) if duration else position,
        "duration": duration,
        "track_key": f"{source}|{artist}|{title}",
        "source": source,
        "playback_status": status_name.lower(),
        "is_playing": is_playing,
        "playback_rate": playback_rate,
        "timeline_updated_at": updated_at,
        "min_seek": min_seek,
        "max_seek": max_seek,
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
        return None
