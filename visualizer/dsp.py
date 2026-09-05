import numpy as np


class SpectrumAnalyzer:
    """Turns raw mono samples into `n_bars` smoothed, log-spaced amplitude
    values in [0, 1] - the same basic idea as cava, with attack/release
    smoothing so bars punch up fast and fall off gently."""

    def __init__(self, sample_rate=44100, chunk_size=2048, n_bars=48,
                 min_freq=40, max_freq=16000, attack=0.65, release=0.12):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.n_bars = n_bars
        self.attack = attack
        self.release = release
        self.window = np.hanning(chunk_size).astype(np.float32)

        freqs = np.fft.rfftfreq(chunk_size, d=1.0 / sample_rate)
        self.freqs = freqs
        max_freq = min(max_freq, sample_rate / 2 - 1)
        edges = np.logspace(np.log10(max(min_freq, 1)), np.log10(max_freq), n_bars + 1)
        self.bin_edges = np.searchsorted(freqs, edges)

        self.smoothed = np.zeros(n_bars, dtype=np.float32)
        self.peaks = np.zeros(n_bars, dtype=np.float32)

        self._bass_avg = 1e-4
        self._beat_cooldown = 0.0

    def resize(self, n_bars):
        if n_bars == self.n_bars:
            return
        self.__init__(self.sample_rate, self.chunk_size, n_bars)

    def process(self, mono_samples, dt=1 / 60):
        n = len(mono_samples)
        if n < self.chunk_size:
            mono_samples = np.pad(mono_samples, (self.chunk_size - n, 0))
        else:
            mono_samples = mono_samples[-self.chunk_size:]

        spectrum = np.abs(np.fft.rfft(mono_samples * self.window))
        raw = np.zeros(self.n_bars, dtype=np.float32)
        for i in range(self.n_bars):
            lo, hi = self.bin_edges[i], self.bin_edges[i + 1]
            if hi <= lo:
                hi = lo + 1
            if lo < len(spectrum):
                raw[i] = spectrum[lo:min(hi, len(spectrum))].mean()

        raw = np.log1p(raw * 6.0)
        m = raw.max()
        if m > 1e-6:
            raw = raw / m

        attack, release = self.attack, self.release
        rising = raw > self.smoothed
        self.smoothed = np.where(
            rising,
            self.smoothed + (raw - self.smoothed) * attack,
            self.smoothed + (raw - self.smoothed) * release,
        )
        self.smoothed = np.clip(self.smoothed, 0.0, 1.0)

        # falling peak-hold markers, useful for a few visualizers
        self.peaks = np.where(self.smoothed > self.peaks, self.smoothed, self.peaks - dt * 0.6)
        self.peaks = np.clip(self.peaks, 0.0, 1.0)

        # crude beat detector from the low bars
        bass = float(self.smoothed[: max(2, self.n_bars // 8)].mean())
        self._bass_avg += (bass - self._bass_avg) * 0.05
        self._beat_cooldown = max(0.0, self._beat_cooldown - dt)
        beat = False
        if bass > self._bass_avg * 1.5 + 0.05 and self._beat_cooldown <= 0:
            beat = True
            self._beat_cooldown = 0.18

        return self.smoothed, self.peaks, beat


def rms(samples):
    if len(samples) == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(samples))))
