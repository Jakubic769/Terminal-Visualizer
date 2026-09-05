from .bars import BarsVisualizer
from .mirror_bars import MirrorBarsVisualizer
from .neon_bars import NeonBarsVisualizer
from .wave import WaveVisualizer
from .circular import CircularVisualizer
from .rings import RingsVisualizer
from .particles import ParticlesVisualizer
from .fire import FireVisualizer
from .dots import DotsGridVisualizer
from .vu import VuMeterVisualizer
from .spectrogram import SpectrogramVisualizer
from .kaleidoscope import KaleidoscopeVisualizer
from .advanced import GENERATED_VISUALIZERS

VISUALIZERS = [
    BarsVisualizer,
    MirrorBarsVisualizer,
    NeonBarsVisualizer,
    WaveVisualizer,
    CircularVisualizer,
    RingsVisualizer,
    ParticlesVisualizer,
    FireVisualizer,
    DotsGridVisualizer,
    VuMeterVisualizer,
    SpectrogramVisualizer,
    KaleidoscopeVisualizer,
    *GENERATED_VISUALIZERS,
]
