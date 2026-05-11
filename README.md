# TuxBellum

> Bellum on Linux. No Windows required.

A GTK4 application that handles everything: GPU detection, Proton setup, Wine prefix configuration, launcher installation, desktop integration — all from one window.

---

## About

I got tired of booting into Windows just to play Bellum. The existing community installer worked but was fragile — a Python GUI shelling out to a Go binary with hardcoded CLI flags and stdin pipes.

TuxBellum is the result of tearing that down and rebuilding it as a single, cohesive GTK4 application. Everything that was spread across three codebases now lives in one Python package. No fragile subprocess calls. Real install progress. Proper error handling.

The name? Tux + Bellum. Seemed obvious.

---

## What TuxBellum Does

- Detects your GPU (NVIDIA, AMD, Intel) and configures everything accordingly
- Downloads and patches Proton-CachyOS with settings optimized for Bellum
- Creates and initializes a WINEPREFIX with all required DLLs
- Downloads the AstarteLauncher and runs it through Proton
- Configures Gamescope, Gamemode, HDR, NVAPI, and FSR 4.1 upgrade path
- Installs desktop shortcuts, app menu entries, and the `Bellum` terminal command

---

## Getting TuxBellum

### AppImage (recommended)

Download the latest AppImage from [Releases](https://github.com/Ch3w3y/tuxbellum/releases/latest):

```bash
chmod +x TuxBellum-*.AppImage
./TuxBellum-*.AppImage
```

### Install Script (curl)

```bash
curl -fsSL https://raw.githubusercontent.com/Ch3w3y/tuxbellum/main/install.sh | bash
```

### AUR (Arch Linux)

```bash
yay -S tuxbellum
```

### Flatpak (coming soon)

```
flatpak install flathub io.github.ch3w3y.tuxbellum
```

### From Source

```bash
git clone https://github.com/Ch3w3y/tuxbellum.git
cd tuxbellum
pip install -e .
tuxbellum
```

---

## Requirements

You'll need these installed on your system:

- **Wine** (11.8 or newer)
- **Winetricks**
- **umu-launcher** (1.3.0 or newer)
- **mesa-utils** (provides glxinfo for GPU detection)

Optionally: Gamescope, Gamemode, MangoHud.

TuxBellum handles everything else — Proton, DLLs, launcher — automatically.

---

## Usage

Launch the GUI:

```bash
tuxbellum
```

Or use the CLI:

```bash
python -m tuxbellum --install --wineprefix /path/to/prefix --fsr41
```

---

## After Installation

Launch Bellum from:
- The desktop shortcut
- Your application menu (Games category)
- Any terminal: `Bellum`

---

## NVIDIA 5000 Series

Driver 595 is broken for UE5 on Wine/Proton — shaders will fail to load. Downgrade to driver 590.

---

## Credits

This project builds directly on the work of **Joe Paji** ([joepaji/bellum-linux-installer](https://github.com/joepaji/bellum-linux-installer)), who created the original Linux installer for Bellum. Joe's project proved it could be done and handled all the hard reverse-engineering of what Bellum needs to run under Wine/Proton. His DXVK patches, winetricks modifications, and FSR integration are bundled here.

TuxBellum is a refactoring and evolution of that work — consolidating the GTK3+Go architecture into a single GTK4 Python application — but the foundations are his.

If you appreciate having Bellum on Linux, consider supporting Joe:

- [Ko-fi](https://ko-fi.com/K3K210EMDU)
- [PayPal](https://www.paypal.com/donate/?business=57PP9DVD3VWAN&no_recurring=0&currency_code=USD)

---

## License

Apache 2.0. See [LICENSE](LICENSE).
