# Command Audit

Every subprocess command executed during install and uninstall. Current as of v3.0.9.

## Legend

| Flag | Meaning |
|---|---|
| ✅ | Return code checked → raises on failure |
| ❌ | Return code not checked → failure silently swallowed |
| ⚠️ | Return code captured but not directly used as pass/fail |
| 🔧 | Intentional ignore (best-effort / cleanup) |

---

## Install Commands

### Precheck Phase

| # | Command | File:Line | Mode | Checked | Notes |
|---|---|---|---|---|---|
| 1 | `wine --version` | `precheck.py` via `run_command_with_output` | capture | ⚠️ | Output parsed; not strictly checked for exit code |
| 2 | `wineboot --version` | `precheck.py` via `run_command_with_output` | capture | ⚠️ | Output parsed |
| 3 | `msidb --version` | `precheck.py` via `run_command_with_output` | capture | ⚠️ | Output parsed |
| 4 | `winecfg --version` | `precheck.py` via `run_command_with_output` | capture | ⚠️ | Output parsed |
| 5 | `wineserver --version` | `precheck.py` via `run_command_with_output` | capture | ⚠️ | Output parsed |
| 6 | `umu-run --version` | `precheck.py:181` via `run_command_with_output` | capture | ✅ | `if "umu-run" not in output` → RuntimeError |
| 7 | `tar -xzf <winetricks.tar.gz> -C <tmp>` | `precheck.py:253` | SILENT | ❌ | Extraction failure not checked; downstream `is_dir(tmp_dir)` always True due to mkdtemp |
| 8 | `sudo make install` (winetricks) | `precheck.py:259` | STREAM | ❌ | Failure not checked; caught later by `look_path("winetricks")` with generic message |
| 9 | `sudo winetricks --self-update` | `precheck.py:265` | STREAM | ✅ | `result = run_command(...); if result != 0: raise RuntimeError(...)` |
| 10 | `lsblk -o NAME,FSTYPE,MOUNTPOINT -J` | `precheck.py` via `run_command_with_output` | capture | ⚠️ | Best-effort; failure returns empty JSON |

### Proton Phase

| # | Command | File:Line | Mode | Checked | Notes |
|---|---|---|---|---|---|
| 11 | `tar -xzf <proton.tar.gz> -C <install_path>` | `proton.py:189` | SILENT | ❌ | Not checked; caught later by `os.path.isfile(archive_path)` |
| 12 | `wget -O <path> <proton_url>` | `proton.py` via `run_command` | SILENT | ⚠️ | Caught by `os.path.isfile` downstream |

### Pipeline Phase (run.py)

| # | Command | File:Line | Mode | Checked | Notes |
|---|---|---|---|---|---|
| 13 | `umu-run wineboot --init` | `wineprefix.py:49-56` | SILENT | ✅ | `if run_command(...) != 0: raise RuntimeError(...)` |
| 14 | `wine msidb -d <msi> ...` | `wineprefix.py:40-46` | SILENT | ✅ | `if run_command(...) != 0: raise RuntimeError(...)` |
| 15 | `winetricks -q vcrun2022` | `wineprefix.py:63-68` | SILENT | ✅ | One check per DLL in loop |
| 16 | `winetricks -q d3dcompiler_47` | `wineprefix.py:63-68` | SILENT | ✅ | |
| 17 | `winetricks -q faudio` | `wineprefix.py:63-68` | SILENT | ✅ | |
| 18 | `winetricks -q dotnet48` | `wineprefix.py:63-68` | SILENT | ✅ | |
| 19 | `winetricks -q mfc140` | `wineprefix.py:63-68` | SILENT | ✅ | |
| 20 | `wineboot --end-session` | `run.py:79` | SILENT | 🔧 | Cleanup; intentional ignore |
| 21 | `wineboot -k` | `run.py:80` | SILENT | 🔧 | Cleanup; intentional ignore |
| 22 | `wineserver -w` | `run.py:81` | SILENT | 🔧 | Cleanup; intentional ignore |
| 23 | `proton run <launcher_exe>` | `run.py:84` | STREAM | ⚠️ | Exit code captured but only used in error message; real check is `os.path.isfile(installed_exe)` |

### DXVK Phase

| # | Command | File:Line | Mode | Checked | Notes |
|---|---|---|---|---|---|
| 24 | `tar -xzf <dxvk.tar.gz> -C <tmp>` | `dxvk.py:28-34` | SILENT | ✅ | `if run_command(...) != 0: raise RuntimeError(...)` |
| 25 | `dxvk_setup.sh install` | `dxvk.py:55-56` | SILENT | ✅ | `if run_command(...) != 0: raise RuntimeError(...)` |
| 26 | `wget -O <cache> <dxvk_url>` | `dxvk.py:94` | SILENT | ✅ | `download_failed = run_command(...) != 0; if download_failed or not os.path.isfile(...)` |

### Tuning Phase

| # | Command | File:Line | Mode | Checked | Notes |
|---|---|---|---|---|---|
| 27 | `winetricks win11` | `run.py:102` via `_check_run` | SILENT | ✅ | |
| 28 | `winetricks grabfullscreen=y windowmanagerdecorated=n mwo=disabled` | `run.py:108` via `_check_run` | SILENT | ✅ | |
| 29 | `winetricks remove_mono` | `run.py:115` via `_check_run` | SILENT | ✅ | AMD only |
| 30 | `wine reg add ... DllOverrides` (d3d12) | `dll_overrides.py:16-29` | SILENT | ❌ | Loop over system DLLs; none checked |
| 31 | `wine reg add ... DllOverrides` (d3d12core) | `dll_overrides.py:16-29` | SILENT | ❌ | |
| 32 | `wine reg add ... DllOverrides` (d3d10core) | `dll_overrides.py:16-29` | SILENT | ❌ | |
| 33 | `wine reg add ... DllOverrides` (d3d9) | `dll_overrides.py:16-29` | SILENT | ❌ | |
| 34 | `wine reg add ... DllOverrides` (d3d8) | `dll_overrides.py:16-29` | SILENT | ❌ | |
| 35 | `wine reg add ... AstarteLauncher.exe\DllOverrides` (d3d11, dxgi) | `dll_overrides.py:33-46` | SILENT | ❌ | |
| 36 | `wine reg add ... Bellum-Win64-Shipping.exe\DllOverrides` (d3d11, dxgi) | `dll_overrides.py:47-60` | SILENT | ❌ | |
| 37 | `wine reg add ... DirectInput RawInput=1` | `run.py:132` via `_check_run` | SILENT | ✅ | |
| 38 | `wineboot --end-session` | `run.py:142` via `_check_run` | SILENT | ✅ | Final cleanup |

### Desktop Integration Phase

| # | Command | File:Line | Mode | Checked | Notes |
|---|---|---|---|---|---|
| 39 | `update-desktop-database <apps_dir>` | `desktop.py:78-81` | SILENT | ❌ | Guarded by `if look_path("update-desktop-database")`; cosmetic |
| 40 | `gio set <desktop_file> metadata::trusted yes` | `desktop.py:85-88` | SILENT | ❌ | Guarded by `if look_path("gio")`; cosmetic |

### Wrapper Script Phase

| # | Command | File:Line | Mode | Checked | Notes |
|---|---|---|---|---|---|
| 41 | `pkexec cp <tmp> /usr/local/bin/Bellum` | `wrappers.py:105` | STREAM | ❌ | Unchecked; silent failure → no launcher |
| 42 | `pkexec chmod 755 /usr/local/bin/Bellum` | `wrappers.py:106` | STREAM | ❌ | Unchecked; crashers on missing file |
| 43 | `pkexec chown <user>:<user> /usr/local/bin/Bellum` | `wrappers.py:111` | STREAM | ❌ | Unchecked; cosmetic |

### FSR Phase (AMD + FSR 4.1 only)

| # | Command | File:Line | Mode | Checked | Notes |
|---|---|---|---|---|---|
| 44 | `mkdir -p <fsr_target_dir>` | `fsr.py:79` | SILENT | ❌ | Subsequent `shutil.copy2` would catch this with a clear error |
| 45 | `wine reg add ... amdxcffx64 override` | `fsr.py:95-107` | SILENT | ❌ | Same pattern as dll_overrides.py; silently swallowed |

### Launcher Download (if not provided)

| # | Command | File:Line | Mode | Checked | Notes |
|---|---|---|---|---|---|
| 46 | `wget -O <cache> <launcher_url>` | `launcher.py:27-30` | SILENT | ⚠️ | Caught by `os.path.isfile(dest)` with generic "download verification failed" |

---

## Uninstall Commands

| # | Command | File:Line | Mode | Checked | Notes |
|---|---|---|---|---|---|
| 47 | `update-desktop-database <apps_dir>` | `uninstall.py:87` | SILENT | ❌ | Cosmetic; stale entries if fails |

---

## Summary

| Status | Count |
|---|---|
| ✅ Checked | 17 |
| ❌ Unchecked (bug) | 14 |
| ⚠️ Partial / downstream check | 6 |
| 🔧 Intentional ignore | 3 |
| **Total** | **40** |
