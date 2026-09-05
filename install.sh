#!/usr/bin/env bash
set -euo pipefail

APP_NAME="visualizer"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/visualizer"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
VENV_DIR="$INSTALL_DIR/venv"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

echo "=============================================="
echo " Terminal Visualizer - Linux installer"
echo "=============================================="

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] Python 3 is not installed."
    echo "Install Python 3.9+ using your distribution package manager."
    exit 1
fi

PYTHON="$(command -v python3)"
PY_VER="$("$PYTHON" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')"
echo "[OK] Python $PY_VER"

# Check Python >= 3.9
if ! "$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,9) else 1)'; then
    echo "[ERROR] Python 3.9 or newer is required."
    exit 1
fi

# Detect package manager and install Linux audio/metadata dependencies.
install_system_deps() {
    if command -v apt-get >/dev/null 2>&1; then
        echo "[INFO] Debian/Ubuntu/Mint detected."
        sudo apt-get update
        sudo apt-get install -y python3 python3-venv python3-pip pulseaudio-utils playerctl
    elif command -v dnf >/dev/null 2>&1; then
        echo "[INFO] Fedora/RHEL/Nobara detected."
        sudo dnf install -y python3 python3-pip pulseaudio-utils playerctl
        # Some Fedora setups need the PipeWire PulseAudio compatibility layer.
        if ! command -v pactl >/dev/null 2>&1; then
            sudo dnf install -y pipewire-pulseaudio || true
        fi
    elif command -v pacman >/dev/null 2>&1; then
        echo "[INFO] Arch-based system detected."
        sudo pacman -Sy --needed --noconfirm python python-pip libpulse playerctl
    elif command -v xbps-install >/dev/null 2>&1; then
        echo "[INFO] Void Linux detected."
        sudo xbps-install -Sy python3 python3-pip pulseaudio-utils playerctl
    elif command -v zypper >/dev/null 2>&1; then
        echo "[INFO] openSUSE detected."
        sudo zypper --non-interactive install python3 python3-pip pulseaudio-utils playerctl
    else
        echo "[WARN] Unknown package manager."
        echo "Install these manually if needed: Python 3.9+, pip, pactl/parec, playerctl."
    fi
}

if [[ "${SKIP_SYSTEM_DEPS:-0}" != "1" ]]; then
    install_system_deps
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

echo "[INFO] Creating isolated Python environment..."
"$PYTHON" -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel

echo "[INFO] Installing Terminal Visualizer and Python dependencies..."
"$VENV_DIR/bin/python" -m pip install "$SCRIPT_DIR"

cat > "$BIN_DIR/$APP_NAME" <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/visualizer" "\$@"
EOF
chmod +x "$BIN_DIR/$APP_NAME"

# Add ~/.local/bin to PATH for common shells, without duplicating it.
add_path_line() {
    local file="$1"
    local line='export PATH="$HOME/.local/bin:$PATH"'
    if [[ -f "$file" ]]; then
        grep -Fqx "$line" "$file" 2>/dev/null || printf '\n%s\n' "$line" >> "$file"
    else
        printf '%s\n' "$line" >> "$file"
    fi
}

case "${SHELL##*/}" in
    zsh)
        add_path_line "$HOME/.zshrc"
        ;;
    fish)
        mkdir -p "$HOME/.config/fish"
        if ! grep -Fqx 'fish_add_path "$HOME/.local/bin"' "$HOME/.config/fish/config.fish" 2>/dev/null; then
            printf '\n%s\n' 'fish_add_path "$HOME/.local/bin"' >> "$HOME/.config/fish/config.fish"
        fi
        ;;
    *)
        add_path_line "$HOME/.bashrc"
        [[ -f "$HOME/.profile" ]] && add_path_line "$HOME/.profile"
        ;;
esac

echo
echo "=============================================="
echo " Installation complete!"
echo "=============================================="
echo "Command: visualizer"
echo
echo "Examples:"
echo "  visualizer"
echo "  visualizer --demo"
echo "  visualizer --all"
echo "  visualizer --list-apps"
echo
echo "Open a NEW terminal (or run: source ~/.bashrc) if"
echo "'visualizer' is not immediately found."
