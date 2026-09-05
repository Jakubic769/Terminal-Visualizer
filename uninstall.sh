#!/usr/bin/env bash
set -euo pipefail
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/visualizer"
BIN="${XDG_BIN_HOME:-$HOME/.local/bin}/visualizer"
rm -f "$BIN"
rm -rf "$INSTALL_DIR"
echo "Terminal Visualizer removed."
echo "If you manually added ~/.local/bin to PATH, you can leave it there."
