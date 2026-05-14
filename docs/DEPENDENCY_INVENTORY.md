# Dependency Inventory

Single source of truth for all dependencies. Updated 2026-05-14 for v3.0.9.

## Categorization

| Category | Meaning | Example |
|---|---|---|
| **bundled** | Shipped inside the release tarball / AppImage / AUR package | FSR DLLs, launcher icon, winetricks mod |
| **downloaded** | Fetched at install time from a remote URL | Proton-CachyOS, DXVK (fallback), Astarte Launcher |
| **system** | Required on the host; checked during precheck | `wine`, `umu-run`, `wget`, `tar` |

---

## Bundled Dependencies

| Dependency | Version | File / Path | Purpose |
|---|---|---|---|
| DXVK (low-latency) | `2.7.1-3-521-low-latency` | `packages/dxvk-2.7.1-3-521-low-latency.tar.gz` | Vulkan-based D3D11/D3D10/D3D9 translation for AMD GPUs |
| Winetricks (modified) | `20250102-modified` | `packages/winetricks-20250102-modified.tar.gz` | DLL/component installer with Bellum-specific patches |
| FSR 4.1 DLLs | — | `packages/fsr4/` | AMD FidelityFX Super Resolution DLLs (`amdxcffx64.dll`, `ffx_fsr4_api_x64.dll`) |
| Launcher icon | — | `packages/launcher_1_256x256x32.png` | Desktop entry / app menu icon |
| Application icon | — | `data/icons/bellum.png` | TuxBellum GTK4 window logo |

**Total bundled size**: ~35 MB (primarily DXVK tarball + FSR DLLs)

---

## Downloaded Dependencies (install-time)

| Dependency | Version / URL | Cached? | Purpose |
|---|---|---|---|
| Proton-CachyOS | `proton-cachyos-10.0-20260424-slr-x86_64` | No (downloaded fresh each install) | Wine + Proton runtime for running Bellum |
| Proton-CachyOS URL | `https://github.com/CachyOS/proton-cachyos/releases/download/<version>/<version>.tar.gz` | — | — |
| DXVK (upstream fallback) | Same version, split on first `-` → `2.7.1` | Yes (`XDG_CACHE_HOME/tuxbellum/dxvk/`) | Fallback when bundled DXVK archive is missing |
| DXVK upstream URL | `https://github.com/doitsujin/dxvk/releases/download/v2.7.1/dxvk-2.7.1.tar.gz` | — | — |
| Astarte Launcher | Latest | Yes (`XDG_CACHE_HOME/tuxbellum/launcher/`) | Bellum's official launcher installer |
| Astarte Launcher URL | `https://auto-updater.astarte.industries/astartelauncher/windows-amd64/AstarteLauncher-amd64-installer.exe` | — | — |
| Winetricks (upstream fallback) | `20250102` | No | Fallback when bundled winetricks is missing; build from source |
| Winetricks upstream URL | `https://github.com/Winetricks/winetricks/archive/refs/tags/20250102.tar.gz` | — | — |

---

## System Dependencies

### Required (checked during prechecks)

| Dependency | Min Version | Check Method | Purpose |
|---|---|---|---|
| `wine` | ≥ 11.0 | `wine --version` | Windows compatibility layer |
| `winetricks` | any | `look_path("winetricks")` | DLL/component installer |
| `umu-run` / `umu-launcher` | ≥ 1.3.0 | `umu-run --version` | Proton container launcher |
| `wget` | any | `look_path("wget")` | HTTP downloads (Proton, launcher) |
| `tar` | any | implicit (called via `run_command`) | Archive extraction |
| `mesa-utils` | any | `look_path("glxinfo")` | GPU detection |

### Optional

| Dependency | Purpose |
|---|---|
| `gamescope` | Compositor for HDR, resolution scaling |
| `gamemode` | CPU/GPU performance governor |
| `mangohud` | In-game performance overlay |

### AUR Package Dependencies

From `PKGBUILD`:

```
depends=(python>=3.11 gtk4 python-gobject wine winetricks wget umu-launcher)
makedepends=(meson python-build python-installer meson-python python-setuptools)
optdepends=(gamescope gamemode mangohud mesa-utils)
```

### AppImage Runtime Dependencies

The AppImage bundles Python, PyGObject, and GTK4 typelibs. The host must provide:

- GTK4 runtime libraries (`.so` files) — shipped by almost all distros
- `wine`, `winetricks`, `umu-launcher`, `mesa-utils`, `wget`, `tar` (same system deps)

### Python Dependencies

| Package | Version | Category | Purpose |
|---|---|---|---|
| `PyGObject` | ≥ 3.50 | runtime | GTK4 Python bindings |
| `meson-python` | ≥ 0.15 | build | Build system |
| `setuptools` | ≥ 61.0 | build | Build system |
| `pytest` | ≥ 7.0 | dev | Test runner |
| `pytest-cov` | ≥ 4.0 | dev | Coverage |
| `pytest-mock` | ≥ 3.10 | dev | Mocking |
| `black` | ≥ 23.0 | dev | Formatter |
| `ruff` | ≥ 0.1.0 | dev | Linter |
| `mypy` | ≥ 1.5 | dev | Type checker |
