"""Reads artist/title/position/duration from Windows' built-in
"Now Playing" system (GlobalSystemMediaTransportControlsSessionManager) -
the same API behind the Windows media overlay / lock screen controls.
Works with Spotify, browsers, most modern media apps automatically."""
import asyncio


async def _get_media_info_async():
    from winsdk.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as MediaManager,
    )

    manager = await MediaManager.request_async()
    session = manager.get_current_session()
    if session is None:
        return None

    info = await session.try_get_media_properties_async()
    timeline = session.get_timeline_properties()

    position = timeline.position.total_seconds()
    duration = (timeline.end_time - timeline.start_time).total_seconds()
    start = timeline.start_time.total_seconds()
    end = timeline.end_time.total_seconds()

    return {
        "artist": info.artist or "Nieznany artysta",
        "title": info.title or "Nieznany tytul",
        "position": max(position, 0.0),
        "duration": max(duration, 0.0),
        "track_key": f"{session.source_app_user_model_id}|{info.artist}|{info.title}|{start:.3f}|{end:.3f}",
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
