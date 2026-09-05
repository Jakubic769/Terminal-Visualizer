import argparse
import platform
import sys


def build_parser():
    p = argparse.ArgumentParser(
        prog="visualizer",
        description="Wizualizator muzyki (jak cava, ale z wiecej stylow, kolorami i paskiem utworu).",
    )
    p.add_argument("--demo", action="store_true",
                   help="Uzyj syntetycznego dzwieku zamiast prawdziwego nasluchu (test bez konfiguracji).")
    p.add_argument("--list-apps", action="store_true", help="Wypisz aplikacje odtwarzajace dzwiek i zakoncz.")
    p.add_argument("--app", type=str, default=None,
                   help="Wybierz aplikacje po (czesciowej) nazwie bez pytania interaktywnie.")
    p.add_argument("--all", action="store_true", help="Sluchaj calego systemu zamiast jednej aplikacji.")
    p.add_argument("--style", type=str, default=None, help="Poczatkowy styl (nazwa lub numer indeksu).")
    p.add_argument("--theme", type=str, default=None, help="Poczatkowy motyw kolorow.")
    p.add_argument("--color", type=str, default=None, help="Wlasny kolor akcentu jako R,G,B np. 255,60,180.")
    p.add_argument("--fps", type=int, default=None, help="Docelowe FPS (domyslnie 60).")
    p.add_argument("--bars", type=int, default=None, help="Liczba slupkow czestotliwosci (domyslnie 48).")
    p.add_argument("--fullscreen", action="store_true", help="Uruchom w pelnym ekranie.")
    return p


def _choose_app_interactively(apps):
    if not apps:
        print("Nie wykryto zadnej aplikacji odtwarzajacej dzwiek w tej chwili.")
        print("Zostanie uzyty dzwiek calego systemu (mozesz wlaczyc muzyke i uruchomic ponownie).")
        return None
    print("\nWybierz zrodlo dzwieku dla wizualizatora:")
    print("  [0] Caly system (wszystkie dzwieki)")
    for i, a in enumerate(apps, start=1):
        detail = a.get("detail") or a.get("pid") or ""
        suffix = f"  ({detail})" if detail else ""
        print(f"  [{i}] {a.get('name', '?')}{suffix}")
    while True:
        try:
            raw = input("Numer > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if raw == "" or raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(apps):
            return apps[int(raw) - 1]
        print("Nieprawidlowy numer, sprobuj ponownie (albo 0 dla calego systemu).")


def main():
    args = build_parser().parse_args()
    system = platform.system()

    apps = []
    capture = None
    metadata_fn = None
    source_label = "system"

    if args.demo:
        from .audio.demo import DemoCapture, list_apps
        apps = list_apps()
        chosen = apps[0]
        capture = DemoCapture(app=chosen)
        source_label = chosen["name"]
        metadata_fn = None

    elif system == "Linux":
        from .audio import linux_pulse as backend
        if not backend.has_pulse_tools():
            print("BLAD: nie znaleziono 'pactl' i/lub 'parec'.")
            print("Zainstaluj np.: sudo apt install pulseaudio-utils   (dziala tez z PipeWire przez pipewire-pulse)")
            sys.exit(1)
        apps = backend.list_apps()

        if args.list_apps:
            _print_apps(apps)
            sys.exit(0)

        chosen = _resolve_choice(args, apps)
        capture = backend.PulseCapture(app=chosen)
        source_label = chosen["name"] if chosen else "caly system"

        from .metadata import linux_playerctl
        if linux_playerctl.available():
            metadata_fn = linux_playerctl.get_metadata
        else:
            print("Wskazowka: zainstaluj 'playerctl' (np. sudo apt install playerctl), "
                  "aby pasek na dole pokazywal artyste/tytul/czas utworu.")

    elif system == "Windows":
        from .audio import windows_wasapi as backend
        apps = backend.list_apps()

        if args.list_apps:
            _print_apps(apps)
            sys.exit(0)

        chosen = _resolve_choice(args, apps)
        if chosen is not None:
            print(f"Uwaga: na Windows izolacja dzwieku dziala przez wyciszenie innych aplikacji "
                  f"na czas dzialania wizualizatora (zostana wyciszone tylko na czas dzialania "
                  f"programu i przywrocone po jego zamknieciu).")
        capture = backend.WasapiCapture(app=chosen)
        source_label = chosen["name"] if chosen else "caly system"

        from .metadata import windows_gsmtc
        metadata_fn = windows_gsmtc.get_metadata

    else:
        print(f"System '{system}' nie jest wspierany (tylko Linux i Windows).")
        print("Mozesz jednak wyprobowac interfejs komenda: visualizer --demo")
        sys.exit(1)

    from .app import run_app
    try:
        run_app(capture, metadata_fn, args, source_label)
    except KeyboardInterrupt:
        pass


def _resolve_choice(args, apps):
    if args.all:
        return None
    if args.app:
        matches = [a for a in apps if args.app.lower() in a.get("name", "").lower()]
        if matches:
            return matches[0]
        print(f"Nie znaleziono aplikacji pasujacej do '{args.app}' - uzyje dzwieku calego systemu.")
        return None
    return _choose_app_interactively(apps)


def _print_apps(apps):
    if not apps:
        print("Brak aktywnych aplikacji odtwarzajacych dzwiek.")
        return
    for a in apps:
        print(f"- {a.get('name')}" + (f"  ({a.get('detail') or a.get('pid')})" if a.get("detail") or a.get("pid") else ""))


if __name__ == "__main__":
    main()
