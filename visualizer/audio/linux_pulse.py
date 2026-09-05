"""Linux audio backend built on PulseAudio / PipeWire-Pulse command line
tools (`pactl`, `parec`). No compiled dependencies needed.

Per-application isolation works "for real" here: every playing app has its
own PulseAudio "sink input", and `parec --monitor-stream=<index>` captures
exactly (and only) that stream - unlike Windows, nothing needs to be muted.
"""
import json
import re
import shutil
import subprocess

import numpy as np


def has_pulse_tools():
    return shutil.which("pactl") is not None and shutil.which("parec") is not None


def list_apps():
    """Returns currently active playback streams as
    [{"name": app name, "index": sink-input index, "detail": media/title}]."""
    apps = []
    try:
        out = subprocess.run(
            ["pactl", "-f", "json", "list", "sink-inputs"],
            capture_output=True, text=True, timeout=2,
        )
        if out.returncode == 0 and out.stdout.strip():
            data = json.loads(out.stdout)
            for item in data:
                props = item.get("properties", {}) or {}
                name = props.get("application.name") or props.get("application.process.binary") or f"stream-{item.get('index')}"
                media = props.get("media.name", "")
                apps.append({"name": name, "index": item.get("index"), "detail": media})
            return apps
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        pass

    # Fallback for older pactl without JSON support.
    try:
        out = subprocess.run(["pactl", "list", "sink-inputs"], capture_output=True, text=True, timeout=2).stdout
    except (subprocess.SubprocessError, OSError):
        return apps
    cur = None
    for line in out.splitlines():
        line = line.strip()
        m = re.match(r"Sink Input #(\d+)", line)
        if m:
            if cur:
                apps.append(cur)
            cur = {"name": "unknown", "index": int(m.group(1)), "detail": ""}
        elif cur is not None and line.startswith("application.name"):
            cur["name"] = line.split("=", 1)[1].strip().strip('"')
        elif cur is not None and line.startswith("media.name"):
            cur["detail"] = line.split("=", 1)[1].strip().strip('"')
    if cur:
        apps.append(cur)
    return apps


class PulseCapture:
    def __init__(self, sample_rate=44100, channels=2, chunk_frames=1024, app=None):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_frames = chunk_frames
        self.sink_input_index = app.get("index") if app else None
        self.proc = None

    def start(self):
        cmd = [
            "parec", "--raw", "--format=s16le",
            f"--rate={self.sample_rate}", f"--channels={self.channels}",
        ]
        if self.sink_input_index is not None:
            cmd.append(f"--monitor-stream={self.sink_input_index}")
        else:
            cmd += ["-d", "@DEFAULT_MONITOR@"]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0)

    def read(self):
        if self.proc is None or self.proc.stdout is None:
            return None
        bytes_needed = self.chunk_frames * self.channels * 2
        buf = bytearray()
        while len(buf) < bytes_needed:
            chunk = self.proc.stdout.read(bytes_needed - len(buf))
            if not chunk:
                if self.proc.poll() is not None:
                    return None
                continue
            buf += chunk
        data = np.frombuffer(bytes(buf), dtype=np.int16).astype(np.float32) / 32768.0
        return data.reshape(-1, self.channels)

    def stop(self):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            self.proc = None
