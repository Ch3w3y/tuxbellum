#!/usr/bin/env bash
# install.sh — TuxBellum installer script
# Usage: curl -fsSL https://raw.githubusercontent.com/Ch3w3y/tuxbellum/main/install.sh | bash
set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

GITHUB_REPO="Ch3w3y/tuxbellum"
INSTALL_DIR="${HOME}/.local/bin"
DATA_DIR="${HOME}/.local/share/tuxbellum"
CONFIG_DIR="${HOME}/.config/tuxbellum"

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# ── Preflight checks ──────────────────────────────────
command -v python3 >/dev/null 2>&1 || error "Python 3.11+ is required but not found."
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
[ "$MAJOR" -gt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 11 ]) || error "Python 3.11+ required, found $PYTHON_VERSION"

command -v pip3 >/dev/null 2>&1 || command -v pip >/dev/null 2>&1 || error "pip is required but not found."

# ── Detect latest release ─────────────────────────────
info "Checking for latest TuxBellum release..."
LATEST=$(curl -fsSL "https://api.github.com/repos/${GITHUB_REPO}/releases/latest" 2>/dev/null \
  | grep '"tag_name"' | head -1 | sed -E 's/.*"v?([^"]+)".*/\1/') \
  || LATEST="3.0.0"

info "Latest version: ${LATEST}"

# ── Install system dependencies ───────────────────────
info "Checking system dependencies..."
DEBIAN_DEPS="python3-gi gir1.2-gtk-4.0 libgtk-4-1"
FEDORA_DEPS="python3-gobject gtk4"
ARCH_DEPS="python-gobject gtk4"

if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq $DEBIAN_DEPS || warn "Some system packages could not be installed."
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf install -y -q $FEDORA_DEPS || warn "Some system packages could not be installed."
elif command -v pacman >/dev/null 2>&1; then
  sudo pacman -S --needed --noconfirm $ARCH_DEPS || warn "Some system packages could not be installed."
else
  warn "Unsupported distro. Install PyGObject and GTK4 manually."
fi

if ! python3 -c "import gi; gi.require_version('Gtk', '4.0')" 2>/dev/null; then
  error "\
GTK4 runtime not available for this Python interpreter ($(python3 -V)).
Your system GTK4 packages are likely installed, but your Python cannot find them.
This happens when using a non-system Python (pyenv, Homebrew, custom build).

Quick fix: use pipx instead:
  pipx install tuxbellum
  tuxbellum

Or install tuxbellum via your package manager (if available):
  Arch:       yay -S tuxbellum
  Flatpak:    flatpak install io.github.ch3w3y.tuxbellum"
fi

# ── Install TuxBellum via pip ─────────────────────────
info "Installing TuxBellum ${LATEST}..."
pip3 install --break-system-packages --user --upgrade "tuxbellum==${LATEST}" 2>/dev/null || \
  pip3 install --break-system-packages --user --upgrade "https://github.com/${GITHUB_REPO}/archive/refs/tags/v${LATEST}.tar.gz"

# ── Install desktop entry ─────────────────────────────
info "Installing desktop entry..."
mkdir -p "${HOME}/.local/share/applications"
cat > "${HOME}/.local/share/applications/tuxbellum.desktop" << 'DESKTOP'
[Desktop Entry]
Name=TuxBellum
Comment=Install, configure, and launch Bellum via Wine/Proton on Linux
Exec=tuxbellum
Type=Application
Icon=bellum
Categories=Game;
Keywords=bellum;tuxbellum;game;wine;proton;launcher;
DESKTOP

# ── Done ──────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}TuxBellum ${LATEST} installed successfully!${NC}"
echo ""
echo "Run it with:  tuxbellum"
echo "Or find it in your application menu under Games."
echo ""
echo "To uninstall: pip3 uninstall tuxbellum"