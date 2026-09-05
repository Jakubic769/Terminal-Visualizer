"""Windows audio backend using WASAPI loopback.

The visualizer is a passive audio consumer: starting it must never mute or
change the volume of any application.  When an application is selected we
record the default output mix, because PyAudioWPatch exposes robust WASAPI
loopback devices but not Windows process-loopback capture.
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
        apps.append({
            "name": proc.name(),
            "pid": proc.pid,
            "detail": "aktywna" if state == 1 else "",
        })
    return apps


class WasapiCapture:
    def __init__(self, sample_rate=44100, channels=2, chunk_frames=1024, app=None):
        self.requested_rate = sample_rate
        self.requested_channels = channels
        self.chunk_frames = chunk_frames
        self.selected_app = app
        self.sample_rate = sample_rate
        self.channels = channels
        self._pyaudio_mod = None
        self.pa = None
        self.stream = None
        self.device = None

    def start(self):
        import pyaudiowpatch as pyaudio
        self._pyaudio_mod = pyaudio

        self.pa = pyaudio.PyAudio()
        try:
            # PyAudioWPatch provides a helper which resolves the loopback
            # device that mirrors the current default WASAPI output.
            default_speakers = self.pa.get_default_wasapi_loopback()
        except AttributeError:
            # Compatibility with older PyAudioWPatch releases.
            wasapi_info = self.pa.get_host_api_info_by_type(pyaudio.paWASAPI)
            output = self.pa.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            default_speakers = None
            if output.get("isLoopbackDevice"):
                default_speakers = output
            else:
                for loopback in self.pa.get_loopback_device_info_generator():
                    if output["name"] in loopback["name"]:
                        default_speakers = loopback
                        break
        except (OSError, LookupError) as exc:
            raise RuntimeError(
                "Nie znaleziono urzadzenia WASAPI loopback dla domyslnego wyjscia audio. "
                "Sprawdz, czy w Windows jest wybrane prawidlowe urzadzenie wyjscia."
            ) from exc

        if not default_speakers:
            raise RuntimeError(
                "Nie znaleziono urzadzenia WASAPI loopback dla domyslnego wyjscia audio."
            )

        self.device = default_speakers
        self.channels = min(
            self.requested_channels,
            int(default_speakers.get("maxInputChannels") or 2),
        ) or 2
        self.sample_rate = int(default_speakers["defaultSampleRate"])

        try:
            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=default_speakers["index"],
                frames_per_buffer=self.chunk_frames,
            )
        except Exception:
            self.stop()
            raise

    def read(self):
        if self.stream is None:
            return None
        try:
            raw = self.stream.read(
                self.chunk_frames,
                exception_on_overflow=False,
            )
        except Exception as exc:
            # Returning None ends the worker cleanly; the main app displays
            # the captured exception instead of silently failing.
            raise RuntimeError(f"Blad odczytu WASAPI loopback: {exc}") from exc

        data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        return data.reshape(-1, self.channels)

    def stop(self):
        try:
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
        except Exception:
            pass
        try:
            if self.pa is not None:
                self.pa.terminate()
        except Exception:
            pass
        self.stream = None
        self.pa = None
        self.device = None
