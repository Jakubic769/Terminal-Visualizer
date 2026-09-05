import queue
import threading
import time

import numpy as np
import pygame

from . import config as cfgmod
from .dsp import SpectrumAnalyzer, rms
from .themes import THEMES, THEME_ORDER, make_custom_theme, normalize_theme
from .viz import VISUALIZERS

ANALYSIS_WINDOW = 2048
WAVE_WINDOW = 900
BOTTOM_BAR_H = 74

HELP_LINES = [
    "TAB / -> nastepny styl   <- poprzedni styl",
    "C zmien motyw kolorow (Shift+C: wstecz)",
    "GORA/DOL: czulosc audio   T: przezroczystosc   Shift+GORA/DOL: czulosc przezroczystosci",
    "[ / ]: czulosc przezroczystosci    F/F11: pelny ekran",
    "H: pokaz/ukryj podpowiedz       ESC/Q: wyjscie",
]


class AudioWorker(threading.Thread):
    def __init__(self, capture):
        super().__init__(daemon=True)
        self.capture = capture
        self.q = queue.Queue(maxsize=8)
        self._stop = threading.Event()
        self.error = None

    def run(self):
        while not self._stop.is_set():
            try:
                chunk = self.capture.read()
            except Exception as e:  # noqa: BLE001
                self.error = e
                break
            if chunk is None:
                break
            try:
                self.q.put_nowait(chunk)
            except queue.Full:
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
                try:
                    self.q.put_nowait(chunk)
                except queue.Full:
                    pass
        try:
            self.capture.stop()
        except Exception:  # noqa: BLE001
            pass

    def stop(self):
        self._stop.set()


class MetadataWorker(threading.Thread):
    def __init__(self, provider):
        super().__init__(daemon=True)
        self.provider = provider
        self.lock = threading.Lock()
        self.data = None
        self.polled_at = 0.0
        self._stop = threading.Event()

    def run(self):
        if self.provider is None:
            return
        while not self._stop.is_set():
            try:
                info = self.provider()
            except Exception:  # noqa: BLE001
                info = None
            now = time.time()
            with self.lock:
                if info is not None:
                    info = dict(info)
                    old = self.data
                    if old:
                        old_key = old.get("track_key") or (old.get("artist"), old.get("title"))
                        new_key = info.get("track_key") or (info.get("artist"), info.get("title"))
                        if old_key == new_key:
                            # GSMTC can briefly report a much older position. Keep the
                            # timeline monotonic instead of jumping 5+ seconds backwards.
                            old_display = old.get("position", 0.0) + max(0.0, now - self.polled_at)
                            new_pos = max(0.0, float(info.get("position", 0.0)))
                            duration_old = float(old.get("duration", 0.0) or 0.0)
                            duration_new = float(info.get("duration", 0.0) or 0.0)
                            near_restart = old_display > 5.0 and new_pos < 2.0
                            large_regression = new_pos + 1.25 < old_display
                            if large_regression and not near_restart:
                                info["position"] = min(old_display, duration_new or old_display)
                            if duration_old > 0.0 and duration_new < duration_old * 0.75:
                                info["duration"] = duration_old
                self.data = info
                self.polled_at = now
            self._stop.wait(1.0)

    def stop(self):
        self._stop.set()

    def get_display_position(self):
        with self.lock:
            data = dict(self.data) if self.data else None
            polled_at = self.polled_at
        if not data:
            return None
        elapsed = max(0.0, time.time() - polled_at)
        pos = float(data.get("position", 0.0)) + elapsed
        duration = float(data.get("duration", 0.0) or 0.0)
        if duration > 0.0:
            pos = min(pos, duration)
        return {
            "artist": data.get("artist", ""),
            "title": data.get("title", ""),
            "position": max(0.0, pos),
            "duration": duration,
        }


def fmt_time(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"


def run_app(capture, metadata_fn, args, source_label):
    pygame.init()
    pygame.display.set_caption("visualizer")
    cfg = cfgmod.load()

    fullscreen = bool(args.fullscreen or cfg.get("fullscreen"))
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((1100, 650), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("consolas,dejavusansmono,monospace", 22)
    font_small = pygame.font.SysFont("consolas,dejavusansmono,monospace", 15)

    n_bars = args.bars or cfg.get("n_bars", 48)
    sample_rate = getattr(capture, "sample_rate", 44100)
    analyzer = SpectrumAnalyzer(sample_rate=sample_rate, chunk_size=ANALYSIS_WINDOW, n_bars=n_bars)

    style_names = [v.name for v in VISUALIZERS]
    style_index = cfg.get("style_index", 0) % len(VISUALIZERS)
    if args.style:
        style_index = _resolve_style(args.style, style_names, style_index)
    visualizers = [cls() for cls in VISUALIZERS]

    custom_rgb = _parse_color(args.color)
    if custom_rgb is None and cfg.get("custom_color") is not None:
        try:
            saved_rgb = tuple(int(v) for v in cfg["custom_color"])
            if len(saved_rgb) == 3 and all(0 <= v <= 255 for v in saved_rgb):
                custom_rgb = saved_rgb
        except (TypeError, ValueError):
            custom_rgb = None
    theme_name = args.theme if args.theme in THEMES else cfg.get("theme", "cava_green")
    if _parse_color(args.color):
        theme_name = "custom"

    sensitivity = float(cfg.get("sensitivity", 1.0))
    transparency_enabled = bool(cfg.get("transparency_enabled", False))
    transparency_sensitivity = float(cfg.get("transparency_sensitivity", 1.0))

    audio_worker = AudioWorker(capture)
    try:
        # Start the native audio backend on the main Python thread.
        # Some PortAudio/WASAPI builds are unreliable when initialization
        # happens from a worker thread.
        capture.start()
    except Exception as exc:  # noqa: BLE001
        audio_worker.error = exc
    audio_worker.start()
    meta_worker = MetadataWorker(metadata_fn)
    meta_worker.start()

    mono_buf = np.zeros(0, dtype=np.float32)
    last_stereo = np.zeros((1, 2), dtype=np.float32)

    t0 = time.time()
    last_t = t0
    running = True
    show_help = True
    help_timer = 6.0

    while running:
        now = time.time()
        dt = max(1e-4, now - last_t)
        last_t = now
        t = now - t0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE and not fullscreen:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key in (pygame.K_RIGHT, pygame.K_TAB):
                    style_index = (style_index + 1) % len(VISUALIZERS)
                elif event.key == pygame.K_LEFT:
                    style_index = (style_index - 1) % len(VISUALIZERS)
                elif event.key == pygame.K_c:
                    back = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
                    theme_name = _cycle_theme(theme_name, back=back)
                    custom_rgb = None
                elif event.key == pygame.K_t:
                    transparency_enabled = not transparency_enabled
                    help_timer = 5.0
                elif event.key == pygame.K_UP:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        transparency_sensitivity = min(3.0, transparency_sensitivity + 0.1)
                    else:
                        sensitivity = min(3.0, sensitivity + 0.1)
                elif event.key == pygame.K_DOWN:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        transparency_sensitivity = max(0.1, transparency_sensitivity - 0.1)
                    else:
                        sensitivity = max(0.2, sensitivity - 0.1)
                elif event.key == pygame.K_LEFTBRACKET:
                    transparency_sensitivity = max(0.1, transparency_sensitivity - 0.1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    transparency_sensitivity = min(3.0, transparency_sensitivity + 0.1)
                elif event.key in (pygame.K_f, pygame.K_F11):
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((1100, 650), pygame.RESIZABLE)
                elif event.key == pygame.K_h:
                    show_help = not show_help
                    help_timer = 999.0 if show_help else 0.0

        drained = False
        try:
            while True:
                chunk = audio_worker.q.get_nowait()
                last_stereo = chunk
                mono = chunk.mean(axis=1).astype(np.float32)
                mono_buf = np.concatenate([mono_buf, mono])
                drained = True
        except queue.Empty:
            pass
        if len(mono_buf) > ANALYSIS_WINDOW * 4:
            mono_buf = mono_buf[-ANALYSIS_WINDOW * 4:]

        if len(mono_buf) >= 64:
            bars, peaks, beat = analyzer.process(mono_buf[-ANALYSIS_WINDOW:], dt)
            wf = mono_buf[-WAVE_WINDOW:]
            waveform = np.pad(wf, (WAVE_WINDOW - len(wf), 0)) if len(wf) < WAVE_WINDOW else wf
        else:
            bars = np.zeros(n_bars)
            peaks = np.zeros(n_bars)
            beat = False
            waveform = np.zeros(WAVE_WINDOW)

        left_rms = rms(last_stereo[:, 0])
        right_rms = rms(last_stereo[:, 1]) if last_stereo.shape[1] > 1 else left_rms

        theme = normalize_theme(make_custom_theme(custom_rgb) if (theme_name == "custom" and custom_rgb) else THEMES.get(theme_name, THEMES["cava_green"]))

        w, h = screen.get_size()
        view_rect = pygame.Rect(0, 0, w, max(1, h - BOTTOM_BAR_H))
        visual_layer = pygame.Surface((view_rect.width, view_rect.height), pygame.SRCALPHA)
        visual_layer.fill((0, 0, 0, 0))

        # The T effect applies to the background only. Visual elements remain
        # fully opaque so bars/lines/particles never become faint.
        if transparency_enabled:
            energy = float(np.mean(np.clip(bars * sensitivity, 0.0, 1.0)))
            # Quiet audio -> more transparent background; loud audio -> more opaque.
            # Sensitivity changes only this background response.
            bg_alpha = int(np.clip(210.0 - energy * 185.0 * transparency_sensitivity, 35.0, 210.0))
            bg_layer = pygame.Surface((view_rect.width, view_rect.height), pygame.SRCALPHA)
            bg_layer.fill((*theme["bg"], bg_alpha))
            screen.fill((0, 0, 0))
            screen.blit(bg_layer, view_rect.topleft)
        else:
            screen.fill(theme["bg"])
        ctx = {
            "rect": view_rect,
            "bars": bars,
            "peaks": peaks,
            "waveform": waveform,
            "stereo_rms": (left_rms, right_rms),
            "beat": beat,
            "theme": theme,
            "t": t,
            "dt": dt,
            "sensitivity": sensitivity,
        }
        visualizers[style_index].draw(visual_layer, ctx)

        # The visualizer layer itself is always opaque. T only changes the
        # background layer drawn above.
        visual_layer.set_alpha(255)
        screen.blit(visual_layer, view_rect.topleft)

        _draw_bottom_bar(screen, w, h, theme, font_big, font_small,
                          meta_worker.get_display_position(), source_label,
                          style_names[style_index], theme_name)

        if show_help and help_timer > 0:
            help_timer -= dt
            _draw_help(screen, font_small, theme)

        if audio_worker.error is not None:
            _draw_error(screen, font_small, str(audio_worker.error))

        pygame.display.flip()
        clock.tick(args.fps or cfg.get("fps", 60))
        _ = drained  # currently unused beyond draining; kept for clarity/future use

    cfg.update({
        "style_index": style_index,
        "theme": theme_name if theme_name != "custom" else cfg.get("theme", "cava_green"),
        "custom_color": list(custom_rgb) if (theme_name == "custom" and custom_rgb) else cfg.get("custom_color"),
        "sensitivity": sensitivity,
        "n_bars": n_bars,
        "fullscreen": fullscreen,
        "transparency_enabled": transparency_enabled,
        "transparency_sensitivity": transparency_sensitivity,
    })
    cfgmod.save(cfg)

    audio_worker.stop()
    meta_worker.stop()
    try:
        audio_worker.join(timeout=1.0)
    except RuntimeError:
        pass
    try:
        capture.stop()
    except Exception:
        pass
    pygame.quit()


def _resolve_style(user_value, style_names, default_index):
    if user_value.isdigit():
        idx = int(user_value)
        if 0 <= idx < len(style_names):
            return idx
        return default_index
    lowered = user_value.lower()
    for i, name in enumerate(style_names):
        if lowered in name.lower():
            return i
    return default_index


def _parse_color(s):
    if not s:
        return None
    try:
        parts = [int(p.strip()) for p in s.split(",")]
        if len(parts) == 3 and all(0 <= p <= 255 for p in parts):
            return tuple(parts)
    except ValueError:
        pass
    return None


def _cycle_theme(current, back=False):
    names = THEME_ORDER
    if current not in names:
        return names[0]
    idx = names.index(current)
    idx = (idx - 1) % len(names) if back else (idx + 1) % len(names)
    return names[idx]


def _elide(font, text, max_w, color):
    surf = font.render(text, True, color)
    if surf.get_width() <= max_w or len(text) <= 1:
        return surf
    while len(text) > 1 and font.render(text + "...", True, color).get_width() > max_w:
        text = text[:-1]
    return font.render(text + "...", True, color)


def _draw_bottom_bar(screen, w, h, theme, font_big, font_small, now_playing, source_label, style_name, theme_key):
    bar_top = h - BOTTOM_BAR_H
    bg = tuple(min(255, c + 8) for c in theme["bg"])
    pygame.draw.rect(screen, bg, (0, bar_top, w, BOTTOM_BAR_H))
    pygame.draw.line(screen, theme.get("secondary") or theme.get("primary", (235, 235, 235)), (0, bar_top), (w, bar_top), 2)

    text_color = theme.get("text", (255, 255, 255))

    if now_playing and (now_playing["artist"] or now_playing["title"]):
        title_line = (f'{now_playing["artist"]} - {now_playing["title"]}'
                       if now_playing["artist"] else now_playing["title"])
        time_line = f'{fmt_time(now_playing["position"])} / {fmt_time(now_playing["duration"]) if now_playing["duration"] else "--:--"}'
        if now_playing["duration"]:
            frac = min(1.0, now_playing["position"] / now_playing["duration"])
            pygame.draw.rect(screen, tuple(int(c * 0.3) for c in theme["primary"]), (12, bar_top + 8, w - 24, 4), border_radius=2)
            pygame.draw.rect(screen, theme["primary"], (12, bar_top + 8, int((w - 24) * frac), 4), border_radius=2)
    else:
        title_line = f"Zrodlo dzwieku: {source_label}"
        time_line = ""

    screen.blit(_elide(font_big, title_line, w - 190, text_color), (12, bar_top + 18))
    if time_line:
        time_surf = font_big.render(time_line, True, text_color)
        screen.blit(time_surf, (w - time_surf.get_width() - 12, bar_top + 18))

    status = f"{style_name}  |  motyw: {theme_key}  |  {source_label}"
    dim = tuple(int(c * 0.7) for c in text_color)
    screen.blit(font_small.render(status, True, dim), (12, bar_top + 48))


def _draw_help(screen, font, theme):
    pad = 10
    w = max(font.size(line)[0] for line in HELP_LINES) + pad * 2
    h = len(HELP_LINES) * 20 + pad * 2
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    text_color = theme.get("text", (255, 255, 255))
    for i, line in enumerate(HELP_LINES):
        overlay.blit(font.render(line, True, text_color), (pad, pad + i * 20))
    screen.blit(overlay, (12, 12))


def _draw_error(screen, font, message):
    screen.blit(font.render(f"Blad przechwytywania dzwieku: {message}", True, (255, 90, 90)), (12, 12))
