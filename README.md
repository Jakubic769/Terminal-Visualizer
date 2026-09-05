# visualizer

Wizualizator muzyki na Linux i Windows - jak `cava`, ale z **12 stylami**,
zmianą kolorów w locie i paskiem "Artysta - Tytul" z czasem utworu na dole.
Instaluje sie jako zwykla komenda: `visualizer`.

Po uruchomieniu program pyta w terminalu, **z jakiej aplikacji ma sluchac
dzwieku** (np. Spotify, Firefox, VLC...) albo pozwala wybrac caly system.

## Style (12 sztuk)

Slupki (Cava) - Slupki lustrzane - Neonowe slupki - Oscyloskop -
Spektrum kolowe - Pulsujace pierscienie - Czasteczki - Ogien -
Siatka LED - VU Metr - Spektrogram - Kalejdoskop

Przelaczanie w trakcie dzialania: `TAB` / `->` / `<-`.

## Kolory

8 gotowych motywow (w tym dynamiczny "Rainbow") przelaczanych klawiszem
`C` (Shift+C - wstecz), albo wlasny kolor z linii komend:
`visualizer --color 255,60,180`. Ustawienia (styl, motyw, czulosc)
zapisuja sie automatycznie i wracaja przy nastepnym uruchomieniu.

## Instalacja

Wymagany Python 3.9+.

### Linux

```bash
# potrzebne narzedzia systemowe do przechwytywania dzwieku per-aplikacja:
sudo apt install pulseaudio-utils   # albo: pipewire-pulse (Fedora/Arch: patrz nizej)
# opcjonalnie, zeby pasek na dole pokazywal artyste/tytul/czas:
sudo apt install playerctl

pip install --user .
```

Fedora: `sudo dnf install pulseaudio-utils playerctl`
Arch: `sudo pacman -S libpulse playerctl` (PipeWire ma to zwykle wbudowane)

Prawdziwa izolacja dzwieku per-aplikacja dziala tu "z automatu" -
kazda aplikacja ma wlasny strumien w PulseAudio/PipeWire i wizualizator
podlacza sie tylko do wybranego strumienia, nic nie trzeba wyciszac.

### Windows

```powershell
pip install .
```

Zainstaluje sie automatycznie: `PyAudioWPatch` (przechwytywanie WASAPI),
`pycaw` (lista aplikacji + glosnosc per-aplikacja) i `winsdk` (odczyt
"teraz odtwarzane" z systemu). Windows 10/11 wymagany.

> **Uwaga o izolacji dzwieku na Windows:** Windows nie ma latwo dostepnego
> w Pythonie API do "prawdziwego" przechwytywania dzwieku pojedynczego
> procesu (Microsoft udostepnia to tylko przez niskopoziomowe C++/WinRT).
> Program uzywa wiec sprawdzonej alternatywy: nagrywa cala petle zwrotna
> systemu, a gdy wybierzesz konkretna aplikacje - **na czas dzialania
> wizualizatora wycisza wszystkie pozostale aplikacje dzwiekowe**, dzieki
> czemu slyszalny (i wizualizowany) zostaje tylko wybrany program.
> Oryginalna glosnosc wszystkich aplikacji wraca automatycznie po
> zamknieciu wizualizatora (rowniez po Ctrl+C). Jesli wolisz nic nie
> wyciszac, wybierz `[0] Caly system` przy starcie albo uruchom z `--all`.

## Uzycie

```bash
visualizer                     # zapyta w terminalu, z jakiej aplikacji sluchac
visualizer --all                # od razu caly system, bez pytania
visualizer --app spotify        # od razu wybierz aplikacje po nazwie
visualizer --list-apps          # tylko wypisz aktywne aplikacje dzwiekowe
visualizer --demo               # tryb demo z syntetycznym dzwiekiem (bez konfiguracji audio)
visualizer --style "Ogien" --theme fire --fullscreen
visualizer --color 0,255,255 --bars 64
```

## Sterowanie w oknie

| Klawisz          | Akcja                              |
|-------------------|-------------------------------------|
| `TAB` / `→` / `←` | zmiana stylu wizualizacji           |
| `C` / `Shift+C`   | zmiana motywu kolorow (wprzod/wstecz) |
| `↑` / `↓`         | czulosc (jak bardzo reaguje na dzwiek) |
| `F` / `F11`       | pelny ekran                         |
| `H`               | pokaz/ukryj podpowiedz z klawiszami |
| `ESC` / `Q`       | wyjscie                             |

## Skad biora sie "Artysta - Tytul" i czas utworu

- **Linux:** przez `playerctl` (MPRIS) - dziala ze Spotify, VLC,
  przegladarkami, mpv i wiekszoscia odtwarzaczy na Linuksie.
- **Windows:** przez wbudowany w system "Now Playing"
  (`GlobalSystemMediaTransportControlsSessionManager`) - to samo API co
  nakladka multimedialna Windows, dziala bez dodatkowej konfiguracji.

Jesli zaden odtwarzacz nie jest wykryty, pasek na dole pokazuje po
prostu wybrane zrodlo dzwieku zamiast tytulu utworu.

## Rozwiazywanie problemow

- **Linux: "nie znaleziono pactl/parec"** - zainstaluj `pulseaudio-utils`
  (dziala tez pod PipeWire przez `pipewire-pulse`).
- **Linux: pasek na dole nie pokazuje utworu** - zainstaluj `playerctl`
  i upewnij sie, ze odtwarzacz obslugujesz MPRIS (wiekszosc obsluguje).
- **Windows: SmartScreen/antywirus przy pierwszym uruchomieniu `pip install`
  kompilujacym pakiety** - to standardowe ostrzezenie dla nowych pakietow
  Pythona, mozna zainstalowac z `--only-binary` jesli sa gotowe kola (wheels).
- Brak dzwieku w ogole / chcesz najpierw sprawdzic interfejs -> `visualizer --demo`.
