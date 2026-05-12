#!/usr/bin/env bash
# build-appimage.sh — Build TuxBellum AppImage
# Requires: Ubuntu 22.04+ with GTK4 dev libraries
set -euo pipefail

VERSION="${1:-$(grep '^version' pyproject.toml | head -1 | sed 's/.*= *["'\'']\([^"'\'']*\)["'\''].*/\1/')}"
APP_NAME="TuxBellum"
WORKDIR="$(mktemp -d)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Building ${APP_NAME} AppImage v${VERSION} ==="

# ── 1. Install build dependencies ─────────────────────
echo "[1/6] Installing dependencies..."
pip install --quiet meson-python build setuptools PyGObject

# ── 2. Build wheel ────────────────────────────────────
echo "[2/6] Building wheel..."
cd "$PROJECT_DIR"
python -m build --wheel --no-isolation 2>/dev/null || \
  pip wheel . --no-deps -w "$WORKDIR/wheels"

# ── 3. Set up AppDir ──────────────────────────────────
echo "[3/6] Setting up AppDir..."
APPDIR="$WORKDIR/AppDir"
mkdir -p "$APPDIR/usr/bin" \
         "$APPDIR/usr/lib/python3/dist-packages" \
         "$APPDIR/usr/share/tuxbellum" \
         "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/metainfo" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Install tuxbellum into AppDir
pip install --prefix="$APPDIR/usr" --no-deps .

# Copy data files (exclude press kit)
cp -r packages/ "$APPDIR/usr/share/tuxbellum/"
rm -rf "$APPDIR/usr/share/tuxbellum/packages/Public Press Kit"
cp -r locales/ "$APPDIR/usr/share/tuxbellum/"
cp data/tuxbellum.desktop "$APPDIR/usr/share/applications/"
cp data/tuxbellum.metainfo.xml "$APPDIR/usr/share/metainfo/"
cp data/icons/bellum.png "$APPDIR/usr/share/icons/hicolor/256x256/apps/tuxbellum.png"

# ── 4. Create AppRun ──────────────────────────────────
echo "[4/6] Creating AppRun..."
cat > "$APPDIR/AppRun" << 'APPRUN'
#!/usr/bin/env bash
SELF=$(readlink -f "$0")
HERE=$(dirname "$SELF")
export PYTHONPATH="$HERE/usr/lib/python3/dist-packages:${PYTHONPATH:-}"
export PATH="$HERE/usr/bin:${PATH:-}"
export GDK_BACKEND=x11
exec "$HERE/usr/bin/tuxbellum" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

# ── 5. Download appimage-builder ──────────────────────
echo "[5/6] Building AppImage..."
# Use linuxdeploy for GTK app bundling
LINUXDEPLOY_URL="https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage"
LINUXDEPLOY_GTK_URL="https://github.com/linuxdeploy/linuxdeploy-plugin-gtk/releases/download/continuous/linuxdeploy-plugin-gtk-x86_64.AppImage"

wget -q "$LINUXDEPLOY_URL" -O "$WORKDIR/linuxdeploy"
wget -q "$LINUXDEPLOY_GTK_URL" -O "$WORKDIR/linuxdeploy-plugin-gtk"
chmod +x "$WORKDIR/linuxdeploy" "$WORKDIR/linuxdeploy-plugin-gtk"

# Build the AppImage
export OUTPUT="${APP_NAME}-${VERSION}-x86_64.AppImage"
cd "$PROJECT_DIR"
export PATH="$WORKDIR:$PATH"
export DEBUG=1

"$WORKDIR/linuxdeploy" \
  --appdir "$APPDIR" \
  --desktop-file "$APPDIR/usr/share/applications/tuxbellum.desktop" \
  --icon-file "$APPDIR/usr/share/icons/hicolor/256x256/apps/tuxbellum.png" \
  --plugin gtk \
  --output appimage

# ── 6. Done ───────────────────────────────────────────
echo "[6/6] Done!"
echo "AppImage: ${PROJECT_DIR}/${APP_NAME}-${VERSION}-x86_64.AppImage"

# Cleanup
rm -rf "$WORKDIR"
