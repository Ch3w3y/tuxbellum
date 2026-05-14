# Owned Paths Audit

Every filesystem path written during install and uninstall. Current as of v3.0.9.

## Legend

| Flag | Meaning |
|---|---|
| 🔒 | Requires root / pkexec |
| 👤 | User-owned |
| 📦 | Inside managed WINEPREFIX |
| 🗑️ | Cleaned by uninstall |

---

## Install-Time Writes

### System Binaries (root-requiring)

| Path | Writer | Flag |
|---|---|---|
| `/usr/local/bin/Bellum` | `wrappers.py:99` via `pkexec cp` | 🔒 🗑️ |

### Desktop Integration (user-owned)

| Path | Writer | Flag |
|---|---|---|
| `~/.local/share/applications/Bellum.desktop` | `desktop.py:28` | 👤 🗑️ |
| `~/Desktop/Bellum.desktop` | `desktop.py:36` | 👤 🗑️ |
| `~/.local/share/icons/hicolor/256x256/apps/bellum.png` | `desktop.py:148` | 👤 🗑️ |
| `~/.config/tuxbellum/games.json` | `main_window.py:26` | 👤 |

### Managed WINEPREFIX

All paths under the user-chosen WINEPREFIX:

| Path | Writer | Flag |
|---|---|---|
| `<WINEPREFIX>/dosdevices/` | `wineprefix.py` (wineboot --init) | 📦 🗑️ |
| `<WINEPREFIX>/drive_c/` | `wineprefix.py` (wineboot --init) | 📦 🗑️ |
| `<WINEPREFIX>/drive_c/users/steamuser/AppData/Local/Astarte Industries/Astarte Launcher/AstarteLauncher.exe` | `run.py:84` (proton run launcher installer) | 📦 🗑️ |
| `<WINEPREFIX>/dxvk.conf` | `dxvk.py:61` (shutil.copy2) | 📦 🗑️ |
| `<WINEPREFIX>/launch_vars.env` | `launch_vars.py` | 📦 🗑️ |
| `<WINEPREFIX>/launcher.log` | wrapper script (at runtime) | 📦 |

### FSR (AMD only, inside WINEPREFIX)

| Path | Writer | Flag |
|---|---|---|
| `<WINEPREFIX>/drive_c/windows/system32/ffx_fsr4_api_x64.dll` | `fsr.py` | 📦 🗑️ |
| `<WINEPREFIX>/drive_c/windows/system32/amdxcffx64.dll` | `fsr.py` | 📦 🗑️ |
| `<WINEPREFIX>/drive_c/windows/system32/ffx_fsr4_api_x64.dll.orig` | `fsr.py` | 📦 🗑️ |
| `<WINEPREFIX>/drive_c/windows/system32/amdxcffx64.dll.orig` | `fsr.py` | 📦 🗑️ |

### Cached Data

| Path | Writer | Flag |
|---|---|---|
| `~/.cache/tuxbellum/launcher/AstarteLauncher-amd64-installer.exe` | `launcher.py:27` | 👤 |
| `~/.cache/tuxbellum/dxvk/dxvk-<version>.tar.gz` | `dxvk.py:94` | 👤 |
| `~/.cache/tuxbellum/logs/installer.log` | `logging.py` | 👤 |
| `~/.local/share/bellum/proton/bellum-<proton_ver>/` | `proton.py` (tar extraction) | 👤 🗑️ |

### Config

| Path | Writer | Flag |
|---|---|---|
| `~/.config/tuxbellum/config.ini` | `manager.py:40` | 👤 |

---

## Uninstall Removals

| Path | Handled by | Method |
|---|---|---|
| `/usr/local/bin/Bellum` | `uninstall.py:64-68` | `os.remove()` |
| `~/.local/share/applications/Bellum.desktop` | `uninstall.py:75-77` | `os.remove()` |
| `~/Desktop/Bellum.desktop` | `uninstall.py:75-77` | `os.remove()` |
| `~/.local/share/icons/hicolor/256x256/apps/bellum.png` | `uninstall.py:83-86` | `os.remove()` |
| `<WINEPREFIX>/` (entire directory) | `uninstall.py:107` | `shutil.rmtree()` |
| `~/.local/share/bellum/proton/` (entire tree) | `uninstall.py:90-99` | `shutil.rmtree()` |

### NOT removed by uninstall

| Path | Reason |
|---|---|
| `~/.config/tuxbellum/config.ini` | Preserved across reinstalls |
| `~/.config/tuxbellum/games.json` | Not cleaned (v4 will replace with manifest) |
| `~/.cache/tuxbellum/` | Cache is non-destructive; user can delete manually |

---

## Summary

| Count | Type |
|---|---|
| 1 | root-requiring path (`/usr/local/bin/Bellum`) |
| 3 | desktop integration paths (`.desktop` ×2 + icon) |
| 6 | managed WINEPREFIX paths |
| 3 | cache paths |
| 1 | config path |
| 9 | paths cleaned by uninstall |
| 3 | paths NOT cleaned by uninstall |
