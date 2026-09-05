"""Windows audio backend.

Real per-process WASAPI "process loopback" capture has no mature Python
binding (only raw C++/Node exist for it), so this uses the well-supported
alternative that real tools use too: capture the full WASAPI loopback of
the default output device (via PyAudioWPatch), and when a single app is
selected, use `pycaw` to temporarily mute every *other* app's session so
only the chosen app's audio reaches the loopback. Original volumes are
always restored on stop()/exit.

If you only want the whole system's audio, pass app=None - nothing gets
muted in that case.
"""
import numpy as np


def list_apps():
    from pycaw.pycaw import AudioUtilities

    apps = []
    seen_pids = set()
    for session in AudioUtilities.GetAllSessions():
        proc = session.Process
        if proc is None:
            continue
        try:
            state = session.State  # 1 == AudioSessionStateActive
        except Exception:
            state = None
        if proc.pid in seen_pids:
            continue
        seen_pids.add(proc.pid)
        apps.append({"name": proc.name(), "pid": proc.pid, "detail": "aktywna" if state == 1 else ""})
    return apps


class WasapiCapture:
    def __init__(self, sample_rate=44100, channels=2, chunk_frames=1024, app=None):
        self.requested_rate = sample_rate
        self.requested_channels = channels
        self.chunk_frames = chunk_frames
        self.isolate_pid = app.get("pid") if app else None
        self.sample_rate = sample_rate
        self.channels = channels
        self._muted = []
        self._pyaudio_mod = None
        self.pa = None
        self.stream = None

    def _mute_other_sessions(self):
        from pycaw.pycaw import AudioUtilities

        if self.isolate_pid is None:
            return
        for session in AudioUtilities.GetAllSessions():
            proc = session.Process
            if proc is None or proc.pid == self.isolate_pid:
                continue
            try:
                vol = session.SimpleAudioVolume
                original = vol.GetMasterVolume()
                vol.SetMasterVolume(0.0, None)
                self._muted.append((vol, original))
            except Exception:
                pass

    def _restore_sessions(self):
        for vol, original in self._muted:
            try:
                vol.SetMasterVolume(original, None)
            except Exception:
                pass
        self._muted = []

    def start(self):
        import pyaudiowpatch as pyaudio
        self._pyaudio_mod = pyaudio

        self.pa = pyaudio.PyAudio()
        wasapi_info = self.pa.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = self.pa.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        if not default_speakers["isLoopbackDevice"]:
            for loopback in self.pa.get_loopback_device_info_generator():
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break

        self.channels = min(self.requested_channels, int(default_speakers["maxInputChannels"]) or 2) or 2
        self.sample_rate = int(default_speakers["defaultSampleRate"])

        if self.isolate_pid is not None:
            self._mute_other_sessions()

        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=default_speakers["index"],
            frames_per_buffer=self.chunk_frames,
        )

    def read(self):
        if self.stream is None:
            return None
        try:
            raw = self.stream.read(self.chunk_frames, exception_on_overflow=False)
        except Exception:
            return None
        data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        return data.reshape(-1, self.channels)

    def stop(self):
        self._restore_sessions()
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
        except Exception:
            pass
        try:
            if self.pa:
                self.pa.terminate()
        except Exception:
            pass
        self.stream = None
        self.pa = None
