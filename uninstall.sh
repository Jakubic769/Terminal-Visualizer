#!/usr/bin/env bash
set -uo pipefail

INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/visualizer"
BIN="${XDG_BIN_HOME:-$HOME/.local/bin}/visualizer"

echo "=============================================="
echo " Terminal Visualizer - Linux uninstaller"
echo "=============================================="
echo

if [[ -f "$BIN" ]]; then
    echo "[INFO] Removing launcher: $BIN"
    rm -f "$BIN"
else
    echo "[INFO] Launcher not found: $BIN"
fi

if [[ -d "$INSTALL_DIR" ]]; then
    echo "[INFO] Removing installation directory: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
    echo "[OK] Terminal Visualizer removed."
else
    echo "[INFO] Installation directory not found: $INSTALL_DIR"
    echo "Nothing to uninstall."
fi

echo
echo "If you manually added ~/.local/bin to PATH, you can leave it there."
