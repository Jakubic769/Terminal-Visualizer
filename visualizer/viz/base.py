class BaseVisualizer:
    """Common interface every style implements.

    ctx (dict) passed to draw() contains:
      rect         - pygame.Rect, the drawable area (above the bottom bar)
      bars         - np.array[n_bars] in [0,1], smoothed spectrum
      peaks        - np.array[n_bars] in [0,1], falling peak-hold values
      waveform     - np.array of recent mono samples in [-1,1]
      stereo_rms   - (left, right) RMS levels, roughly [0,1]
      beat         - bool, True on detected beat/kick this frame
      theme        - dict, see themes.py
      t            - float, seconds since start
      dt           - float, seconds since last frame
      sensitivity  - float multiplier the user can adjust live
    """

    name = "Base"

    def draw(self, surf, ctx):
        raise NotImplementedError
