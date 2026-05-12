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
echo "[1/7] Installing dependencies..."
pip install --quiet meson-python build setuptools PyGObject

# ── 2. Build wheel ────────────────────────────────────
echo "[2/7] Building wheel..."
cd "$PROJECT_DIR"
python -m build --wheel --no-isolation 2>/dev/null || \
  pip wheel . --no-deps -w "$WORKDIR/wheels"

# ── 3. Set up AppDir ──────────────────────────────────
echo "[3/7] Setting up AppDir..."
APPDIR="$WORKDIR/AppDir"
mkdir -p "$APPDIR/usr/bin" \
         "$APPDIR/usr/lib/python3/dist-packages" \
         "$APPDIR/usr/share/tuxbellum" \
         "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/metainfo" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Install tuxbellum into AppDir
python3 -m pip install --prefix="$APPDIR/usr" --no-deps . --force-reinstall

# Discover where pip installed the package
# (dist-packages on Debian/Ubuntu, site-packages on other distros)
PKG_DIR=$(find "$APPDIR/usr/lib" -maxdepth 4 -path "*/tuxbellum" -type d 2>/dev/null | head -1)
if [ -n "$PKG_DIR" ]; then
    PKG_DIR=$(dirname "$PKG_DIR")  # Parent = the packages directory
else
    echo "ERROR: Could not find tuxbellum install location" >&2
    exit 1
fi
echo "  Package directory: $PKG_DIR"

# Compute path relative to APPDIR for AppRun
REL_PKG_DIR="${PKG_DIR#"$APPDIR"}"

# Copy data files (exclude press kit)
cp -r packages/ "$APPDIR/usr/share/tuxbellum/"
rm -rf "$APPDIR/usr/share/tuxbellum/packages/Public Press Kit"
cp -r locales/ "$APPDIR/usr/share/tuxbellum/"
cp data/tuxbellum.desktop "$APPDIR/usr/share/applications/"
cp data/tuxbellum.metainfo.xml "$APPDIR/usr/share/metainfo/"
cp data/icons/bellum.png "$APPDIR/usr/share/icons/hicolor/256x256/apps/tuxbellum.png"

# ── 4. Bundle GTK4 typelib files (version-agnostic) ────
echo "[4/7] Bundling GTK4 typelib files..."
# Find girepository directory
GIREPO_DIR=""
for candidate in /usr/lib/girepository-1.0 \
                 /usr/lib/x86_64-linux-gnu/girepository-1.0 \
                 /usr/lib64/girepository-1.0; do
    if [ -d "$candidate" ] && [ -f "$candidate/Gtk-4.0.typelib" ]; then
        GIREPO_DIR="$candidate"
        break
    fi
done

if [ -z "$GIREPO_DIR" ]; then
    echo "ERROR: Could not find girepository with Gtk-4.0.typelib" >&2
    exit 1
fi
echo "  girepository: $GIREPO_DIR"

mkdir -p "$APPDIR/usr/lib/girepository-1.0"
cp -a "$GIREPO_DIR"/*.typelib "$APPDIR/usr/lib/girepository-1.0/"
echo "  Bundled $(ls "$APPDIR/usr/lib/girepository-1.0/"*.typelib 2>/dev/null | wc -l) typelib files"
echo "  Note: native .so NOT bundled — host must have GTK4 installed"

# ── 5. Create AppRun ──────────────────────────────────
echo "[5/7] Creating AppRun..."
cat > "$APPDIR/AppRun" << APPRUN
#!/usr/bin/env bash
set -e
SELF=\$(readlink -f "\$0")
HERE=\$(dirname "\$SELF")
export PYTHONPATH="\$HERE${REL_PKG_DIR}:\${PYTHONPATH:-}"
export PATH="\$HERE/usr/bin:\${PATH:-}"
export GDK_BACKEND=x11
export GI_TYPELIB_PATH="\$HERE/usr/lib/girepository-1.0"
exec python3 "\$HERE/usr/bin/tuxbellum" "\$@"
APPRUN
chmod +x "$APPDIR/AppRun"

# ── 6. Download appimagetool and build AppImage ───────
echo "[6/7] Building AppImage..."
APPIMAGETOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
wget --tries=3 --progress=dot:mega "$APPIMAGETOOL_URL" -O "$WORKDIR/appimagetool"
chmod +x "$WORKDIR/appimagetool"

# Symlink desktop file and icon to AppDir root (required by appimagetool)
cp "$APPDIR/usr/share/applications/tuxbellum.desktop" "$APPDIR/tuxbellum.desktop"
cp "$APPDIR/usr/share/icons/hicolor/256x256/apps/tuxbellum.png" "$APPDIR/bellum.png"

# Debug: show AppDir root
echo "--- AppDir root ---"
ls "$APPDIR"

# Build the AppImage
export OUTPUT="${APP_NAME}-${VERSION}-x86_64.AppImage"
cd "$PROJECT_DIR"
ARCH=x86_64 "$WORKDIR/appimagetool" "$APPDIR" "$OUTPUT"

# ── 7. Done ───────────────────────────────────────────
echo "[7/7] Done!"
echo "AppImage: ${PROJECT_DIR}/${APP_NAME}-${VERSION}-x86_64.AppImage"

# Cleanup
rm -rf "$WORKDIR"
