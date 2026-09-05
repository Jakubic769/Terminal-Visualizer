# Terminal Visualizer

> A colorful real-time music visualizer for your terminal, inspired by [Cava](https://github.com/karlstav/cava).

**62 visualization styles • 33 color themes • live switching • per-app audio selection • track metadata • Linux & Windows**

![Terminal Visualizer](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-111827?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

## ✨ Features

- 🎵 Real-time terminal audio visualization
- 🎨 **62 visualization styles** (12 core + 50 premium)
- 🌈 **33 color themes**, including dynamic Rainbow
- 🎛️ Change styles and themes while the visualizer is running
- 🎧 Select a specific audio application or visualize the entire system
- 🎼 Show artist, title, and playback time when metadata is available
- 🖥️ Fullscreen mode
- ⚙️ Persistent settings for style, theme, and sensitivity
- 🧪 Built-in demo mode that works without audio configuration
- 🐧 Linux support with PulseAudio/PipeWire
- 🪟 Windows 10/11 support with WASAPI
- 🚀 One-command installation with automatic dependency setup and PATH configuration

## 🎨 Visualization Styles

1. Bars (Cava)
2. Mirror Bars
3. Neon Bars
4. Oscilloscope
5. Color Spectrum
6. Pulsing Rings
7. Particles
8. Fire
9. LED Grid
10. VU Meter
11. Spectrogram
12. Kaleidoscope

Switch styles live with `TAB`, `←`, or `→` — the core styles remain available alongside 50 premium, art-directed styles.

### Premium styles

The 50 additional styles are designed as distinct visual compositions rather than simple geometry variations:

`Aurora Ribbon` · `Glass Wave` · `Spectrum Horizon` · `Prism Wave` · `Pulse Rail` · `Luminous Columns` · `Cathedral` · `Monument` · `Blade Array` · `Pillars Pro` · `Orbit Halo` · `Planetary` · `Solar System` · `Eclipse` · `Saturn` · `Pulse Rings` · `Ripple Rings` · `Concentric Glass` · `Core Reactor` · `Quantum Ring` · `Nebula` · `Star Drift` · `Comet Field` · `Particle Bloom` · `Gravity Well` · `Kaleido Prime` · `Kaleido Glass` · `Lotus` · `Mandala` · `Orbit Flower` · `Laser Sweep` · `Radar Bloom` · `Scope` · `Scanner Grid` · `Hologrid` · `Wireframe City` · `Tunnel Glass` · `Infinite Hall` · `Perspective Grid` · `Deep Tunnel` · `Crystal Shards` · `Facet` · `Prism Core` · `Diamond Pulse` · `Fractal Bloom` · `Signal Bloom` · `Oscillo Pro` · `Waveform Pro` · `Frequency Lens` · `Afterglow`.

### Transparency effect

Press `T` to toggle audio-reactive background transparency. Only the background layer changes; bars, waves, particles, rings and other visual elements remain fully opaque.

- `[` / `]` — lower / raise transparency sensitivity
- `Shift` + `↑` / `↓` — lower / raise transparency sensitivity
- `↑` / `↓` — change normal audio sensitivity

## 🌈 Color Themes

Switch themes while running with `C` and `Shift+C`.

You can also choose a custom RGB color:

```bash
visualizer --color 255,60,180
```

## 🚀 Installation

### Linux

The easiest method is the included installer:

```bash
chmod +x install.sh
./install.sh
```

The installer automatically:

- detects your package manager (`apt`, `dnf`, `pacman`, `xbps`, or `zypper`)
- installs required system audio/metadata tools
- creates an isolated Python virtual environment
- installs the Python dependencies
- creates the `visualizer` command
- adds the required user bin directory to your `PATH`

Then open a new terminal and run:

```bash
visualizer
```

#### Manual Linux installation

**Debian / Ubuntu:**

```bash
sudo apt install pulseaudio-utils playerctl python3 python3-pip python3-venv
pip install --user .
```

**Fedora / Nobara:**

```bash
sudo dnf install pulseaudio-utils playerctl python3 python3-pip
pip install --user .
```

**Arch Linux:**

```bash
sudo pacman -S libpulse playerctl python python-pip
pip install --user .
```

> PipeWire users can use `pipewire-pulse`, which provides the PulseAudio-compatible interface required by the visualizer.

### Windows 10/11

**Python 3.9-3.12 is required for the current Windows build.** The Windows audio/metadata dependencies used by this release include `winsdk`, whose published Windows wheels currently go up to CPython 3.12.

Run:

```bat
install.bat
```

The installer automatically:

- checks for a compatible Python 3.9-3.12 installation
- creates a dedicated virtual environment
- installs the required Python packages
- creates `visualizer.cmd`
- adds the launcher directory to your **User PATH**

Open a new terminal after installation and run:

```bat
visualizer
```

## 🎧 Audio Sources

When launched normally, Terminal Visualizer lets you choose what to visualize:

```text
[0] Entire system
[1] Spotify
[2] Firefox
[3] VLC
...
```

You can skip the selection menu with:

```bash
visualizer --all
```

Or select an application directly:

```bash
visualizer --app spotify
```

List currently available audio applications:

```bash
visualizer --list-apps
```

### Windows audio capture

Windows uses WASAPI loopback to capture the audio currently being played by the default output device. Starting the visualizer **never mutes or changes the volume of other applications**.

When you choose a specific application, its name is used as the selected source label, but the current Python backend still captures the output mix. True per-process loopback requires the Windows process-loopback API, which is separate from the ordinary device loopback API.

If you want to visualize the whole system directly, use:

```bash
visualizer --all
```

## 🎼 Track Information

Terminal Visualizer can display information such as:

```text
Artist - Track Title                         02:41 / 04:12
```

### Linux

Metadata is read through **MPRIS** using `playerctl`. This works with Spotify, VLC, browsers, mpv, and many other media players.

### Windows

Metadata is read through Windows' **Global System Media Transport Controls** API, the same system media infrastructure used by Windows' media controls.

## 🎮 Controls

| Key | Action |
|---|---|
| `TAB` / `→` / `←` | Change visualization style |
| `C` / `Shift+C` | Change color theme |
| `↑` / `↓` | Adjust audio sensitivity |
| `F` / `F11` | Toggle fullscreen |
| `H` | Show/hide keyboard help |
| `ESC` / `Q` | Quit |

## 🧪 Demo Mode

Want to test the visuals without configuring audio first?

```bash
visualizer --demo
```

This generates synthetic audio data and lets you explore the interface immediately.

## 🛠️ Command Examples

```bash
# Interactive audio source selection
visualizer

# Visualize the entire system immediately
visualizer --all

# Select an application
visualizer --app spotify

# List available applications
visualizer --list-apps

# Demo mode
visualizer --demo

# Start with a specific style and theme
visualizer --style "Fire" --theme fire --fullscreen

# Custom RGB color
visualizer --color 0,255,255 --bars 64
```

## 🔧 Troubleshooting

### `pactl` or `parec` not found on Linux

Install the PulseAudio compatibility utilities:

```bash
# Debian / Ubuntu
sudo apt install pulseaudio-utils

# Fedora / Nobara
sudo dnf install pulseaudio-utils

# Arch
sudo pacman -S libpulse
```

If you use PipeWire, make sure the PulseAudio compatibility layer is installed and running.

### Track information is missing on Linux

Install `playerctl`:

```bash
sudo apt install playerctl
```

or the equivalent package for your distribution.

### No audio / black visualizer

First test the interface independently from your audio setup:

```bash
visualizer --demo
```

If demo mode works, the issue is most likely related to the selected audio source or system audio configuration.

### Windows installation issues

Make sure Python 3.9-3.12 is installed and available from the terminal:

```bat
python --version
```

If several Python versions are installed, `install.bat` will automatically prefer 3.12, then 3.11, 3.10, or 3.9.

Then run the installer again:

```bat
install.bat
```

## 🗑️ Uninstallation

### Linux

```bash
./uninstall.sh
```

### Windows

```bat
uninstall.bat
```

The uninstallers remove the dedicated environment and launcher created by the installers.

> If you installed the package manually with `pip`, uninstall it separately with `pip uninstall`.

## 📁 Project Structure

```text
Terminal-Visualizer/
├── visualizer/              # Application source
├── install.sh               # Linux installer
├── install.bat              # Windows installer
├── uninstall.sh             # Linux uninstaller
├── uninstall.bat            # Windows uninstaller
├── pyproject.toml           # Python package configuration
├── test_render.py           # Rendering tests
└── README.md
```

## 🤝 Contributing

Pull requests, bug reports, ideas, and new visualization styles are welcome.

1. Fork the repository
2. Create a branch
3. Make your changes
4. Test them on your platform
5. Open a pull request

If you add a new visualization style, please keep the existing keyboard controls and terminal performance in mind.

## 📜 License

This project is released under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

Made for people who think a terminal should be allowed to have a little rhythm. 🎧⚡

## Nowe sterowanie i efekty

Wizualizator zawiera teraz 50 dodatkowych stylów (łącznie 62) oraz 25 dodatkowych motywów kolorystycznych.

- `T` — włącza/wyłącza audio-reaktywny efekt przezroczystości.
- `[` / `]` — zmniejsza/zwiększa czułość przezroczystości.
- `Shift` + `Góra/Dół` — zmniejsza/zwiększa czułość przezroczystości.
- `Góra/Dół` — nadal steruje czułością audio.
- Pozycja utworu jest wygładzana, aby chwilowe błędne odczyty Windows GSMTC nie cofały licznika. Czas trwania jest stabilizowany dla bieżącego utworu.

