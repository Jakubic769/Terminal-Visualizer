#!/usr/bin/env bash
set -uo pipefail

APP_NAME="visualizer"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/visualizer"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
VENV_DIR="$INSTALL_DIR/venv"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$INSTALL_DIR/install.log"

# ============================================================
# Logging helpers
# ============================================================
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    mkdir -p "$INSTALL_DIR"
    echo "$msg" >> "$LOG_FILE"
}

log "=============================================="
log " Terminal Visualizer - Linux Installer"
log "=============================================="

# ============================================================
# 1. Find Python 3.9+
# ============================================================
log "[INFO] Searching for Python 3.9+..."

PYTHON=""

for cmd in python3 python3.13 python3.12 python3.11 python3.10 python3.9; do
    if command -v "$cmd" >/dev/null 2>&1; then
        if "$cmd" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,9) else 1)' 2>/dev/null; then
            PYTHON="$(command -v "$cmd")"
            log "[OK] Found Python: $PYTHON"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    log "[ERROR] Python 3.9+ not found. Install it with your package manager."
    exit 1
fi

PY_VER="$("$PYTHON" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')"
log "[OK] Python version: $PY_VER"

# Check venv module
if ! "$PYTHON" -m venv --help >/dev/null 2>&1; then
    log "[ERROR] Python 'venv' module is missing. Install python3-venv."
    exit 1
fi

# ============================================================
# 2. Install system dependencies (best effort, never fatal)
# ============================================================
install_system_deps() {
    log "[INFO] Installing system dependencies..."
    local failed=0

    if command -v apt-get >/dev/null 2>&1; then
        log "[INFO] Detected: apt-get (Debian/Ubuntu/Mint)"
        sudo apt-get update >> "$LOG_FILE" 2>&1 || failed=1
        sudo apt-get install -y python3-venv python3-pip pulseaudio-utils playerctl >> "$LOG_FILE" 2>&1 || failed=1

    elif command -v dnf >/dev/null 2>&1; then
        log "[INFO] Detected: dnf (Fedora/RHEL/Nobara)"
        sudo dnf install -y python3-pip pulseaudio-utils playerctl >> "$LOG_FILE" 2>&1 || failed=1
        if ! command -v pactl >/dev/null 2>&1; then
            sudo dnf install -y pipewire-pulseaudio >> "$LOG_FILE" 2>&1 || true
        fi

    elif command -v pacman >/dev/null 2>&1; then
        log "[INFO] Detected: pacman (Arch)"
        sudo pacman -Sy --needed --noconfirm python python-pip libpulse playerctl >> "$LOG_FILE" 2>&1 || failed=1

    elif command -v xbps-install >/dev/null 2>&1; then
        log "[INFO] Detected: xbps (Void Linux)"
        sudo xbps-install -Sy python3 python3-pip pulseaudio-utils playerctl >> "$LOG_FILE" 2>&1 || failed=1

    elif command -v zypper >/dev/null 2>&1; then
        log "[INFO] Detected: zypper (openSUSE)"
        sudo zypper --non-interactive install python3 python3-pip pulseaudio-utils playerctl >> "$LOG_FILE" 2>&1 || failed=1

    else
        log "[WARN] Unknown package manager. Install manually: python3-venv, pip, pactl/parec, playerctl."
        failed=1
    fi

    if [[ $failed -eq 1 ]]; then
        log "[WARN] Some system packages may have failed to install. Continuing anyway..."
    fi
}

if [[ "${SKIP_SYSTEM_DEPS:-0}" != "1" ]]; then
    install_system_deps
fi

# ============================================================
# 3. Prepare directories
# ============================================================
mkdir -p "$INSTALL_DIR" "$BIN_DIR"

# ============================================================
# 4. Create virtual environment
# ============================================================
log "[INFO] Creating virtual environment at $VENV_DIR..."

if [[ -f "$VENV_DIR/bin/python" ]]; then
    log "[INFO] Existing venv found, reusing."
else
    "$PYTHON" -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1
    if [[ $? -ne 0 ]]; then
        log "[ERROR] Failed to create virtual environment."
        exit 1
    fi
    log "[OK] Virtual environment created."
fi

if [[ ! -f "$VENV_DIR/bin/python" ]]; then
    log "[ERROR] venv/bin/python missing after creation."
    exit 1
fi

# ============================================================
# 5. Upgrade pip
# ============================================================
log "[INFO] Upgrading pip, setuptools, wheel..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel >> "$LOG_FILE" 2>&1
if [[ $? -ne 0 ]]; then
    log "[WARN] pip upgrade had issues, continuing..."
else
    log "[OK] pip upgraded."
fi

# ============================================================
# 6. Install Terminal Visualizer
# ============================================================
log "[INFO] Installing Terminal Visualizer from $SCRIPT_DIR..."

if [[ -f "$SCRIPT_DIR/pyproject.toml" ]]; then
    "$VENV_DIR/bin/python" -m pip install "$SCRIPT_DIR" >> "$LOG_FILE" 2>&1
elif [[ -f "$SCRIPT_DIR/setup.py" ]]; then
    "$VENV_DIR/bin/python" -m pip install "$SCRIPT_DIR" >> "$LOG_FILE" 2>&1
else
    log "[ERROR] No pyproject.toml or setup.py found in $SCRIPT_DIR"
    exit 1
fi

if [[ $? -ne 0 ]]; then
    log "[ERROR] pip install failed. Check $LOG_FILE for details."
    echo "[ERROR] Installation failed. See log: $LOG_FILE"
    exit 1
fi

log "[OK] Package installed."

# ============================================================
# 7. Detect entry point and create launcher
# ============================================================
log "[INFO] Creating command launcher..."

ENTRY_CMD=""

if [[ -f "$VENV_DIR/bin/visualizer" ]]; then
    ENTRY_CMD="$VENV_DIR/bin/visualizer"
    log "[OK] Found entry point script: $ENTRY_CMD"
elif [[ -f "$VENV_DIR/bin/visualizer.exe" ]]; then
    ENTRY_CMD="$VENV_DIR/bin/visualizer.exe"
    log "[OK] Found entry point exe: $ENTRY_CMD"
else
    ENTRY_CMD="$VENV_DIR/bin/python -m visualizer.cli"
    log "[INFO] No entry point found, using fallback: python -m visualizer.cli"
fi

cat > "$BIN_DIR/$APP_NAME" <<EOF
#!/usr/bin/env bash
exec $ENTRY_CMD "\$@"
EOF

chmod +x "$BIN_DIR/$APP_NAME"

if [[ ! -x "$BIN_DIR/$APP_NAME" ]]; then
    log "[ERROR] Could not create launcher at $BIN_DIR/$APP_NAME"
    exit 1
fi

log "[OK] Launcher created: $BIN_DIR/$APP_NAME"

# ============================================================
# 8. Add to PATH
# ============================================================
log "[INFO] Checking PATH configuration..."

add_path_line() {
    local file="$1"
    local line='export PATH="$HOME/.local/bin:$PATH"'
    if [[ -f "$file" ]]; then
        if ! grep -Fqx "$line" "$file" 2>/dev/null; then
            printf '\n%s\n' "$line" >> "$file"
            log "[OK] Updated $file"
        fi
    else
        printf '%s\n' "$line" >> "$file"
        log "[OK] Created $file"
    fi
}

# Detect shell
current_shell="${SHELL##*/}"
if [[ -z "$current_shell" ]] || [[ "$current_shell" == "sh" ]]; then
    if [[ -n "$BASH_VERSION" ]]; then
        current_shell="bash"
    elif [[ -n "$ZSH_VERSION" ]]; then
        current_shell="zsh"
    else
        current_shell="bash"
    fi
fi

case "$current_shell" in
    zsh)
        add_path_line "$HOME/.zshrc"
        ;;
    fish)
        mkdir -p "$HOME/.config/fish"
        fish_config="$HOME/.config/fish/config.fish"
        fish_line='fish_add_path "$HOME/.local/bin"'
        if [[ -f "$fish_config" ]]; then
            if ! grep -Fqx "$fish_line" "$fish_config" 2>/dev/null; then
                printf '\n%s\n' "$fish_line" >> "$fish_config"
                log "[OK] Updated $fish_config"
            fi
        else
            printf '%s\n' "$fish_line" >> "$fish_config"
            log "[OK] Created $fish_config"
        fi
        ;;
    *)
        add_path_line "$HOME/.bashrc"
        [[ -f "$HOME/.profile" ]] && add_path_line "$HOME/.profile"
        ;;
esac

# ============================================================
# 9. Verify
# ============================================================
log "[INFO] Verifying installation..."

if "$BIN_DIR/$APP_NAME" --help >/dev/null 2>&1; then
    log "[OK] 'visualizer --help' works."
else
    log "[WARN] 'visualizer --help' returned non-zero, but installation may still work."
fi

# ============================================================
# 10. Done
# ============================================================
log "=============================================="
log " Installation complete!"
log "=============================================="

echo
echo "=============================================="
echo " Installation complete!"
echo "=============================================="
echo "Command:     visualizer"
echo "Log file:     $LOG_FILE"
echo "Install dir:  $INSTALL_DIR"
echo
echo "Examples:"
echo "  visualizer"
echo "  visualizer --demo"
echo "  visualizer --all"
echo
echo ">>> IMPORTANT: Open a NEW terminal window <<<"
echo "    (or run: source ~/.bashrc / source ~/.zshrc)"
echo
echo "If 'visualizer' is not found, run directly:"
echo "  $BIN_DIR/$APP_NAME --demo"